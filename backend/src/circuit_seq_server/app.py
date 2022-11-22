from __future__ import annotations
import secrets
import pathlib
import datetime
import flask
from flask import Flask
from flask import jsonify
from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from circuit_seq_server.logger import get_logger
from circuit_seq_server.date_utils import get_start_of_week
from circuit_seq_server.model import (
    db,
    Sample,
    User,
    add_new_user,
    add_new_sample,
    remaining_samples_this_week,
    get_current_settings,
    set_current_settings,
    update_samples_zipfile,
    process_result,
    _add_temporary_users_for_testing,
    _add_temporary_samples_for_testing,
)


def create_app(data_path: str = "/circuit_seq_data"):
    app = Flask("CircuitSeqServer")
    # new secret key on server restart -> invalidates all existing tokens
    app.config["JWT_SECRET_KEY"] = secrets.token_urlsafe(64)
    # tokens are by default valid for 30mins
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=30)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{data_path}/CircuitSeq.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # limit max file upload size to 64mb
    app.config["MAX_CONTENT_LENGTH"] = 64 * 1024 * 1024
    app.config["CIRCUITSEQ_DATA_PATH"] = data_path

    CORS(app)  # todo: limit ports / routes

    jwt = JWTManager(app)
    db.init_app(app)
    logger = get_logger("CircuitSeqServer")

    # https://flask-jwt-extended.readthedocs.io/en/stable/api/#flask_jwt_extended.JWTManager.user_identity_loader
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    # https://flask-jwt-extended.readthedocs.io/en/stable/api/#flask_jwt_extended.JWTManager.user_lookup_loader
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.execute(
            db.select(User).filter(User.id == identity)
        ).scalar_one_or_none()

    @app.route("/login", methods=["POST"])
    def login():
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        logger.info(f"Login request from {email}")
        user = db.session.execute(
            db.select(User).filter(User.email == email)
        ).scalar_one_or_none()
        if not user:
            logger.info(f"  -> user not found")
            return jsonify("Unknown email address"), 401
        if not user.activated:
            logger.info(f"  -> user not activated")
            return jsonify("User account is not yet activated"), 401
        if not user.check_password(password):
            logger.info(f"  -> wrong password")
            return jsonify("Incorrect password"), 401
        logger.info(f"  -> returning JWT access token")
        access_token = create_access_token(identity=user)
        return jsonify(user=user.as_dict(), access_token=access_token)

    @app.route("/signup", methods=["POST"])
    def signup():
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        logger.info(f"Signup request from {email}")
        message, code = add_new_user(email, password)
        return jsonify(message=message), code

    @app.route("/remaining", methods=["GET"])
    def remaining():
        return jsonify(remaining=remaining_samples_this_week())

    @app.route("/running_options", methods=["GET"])
    @jwt_required()
    def running_options():
        settings = get_current_settings()
        return jsonify(running_options=settings["running_options"])

    @app.route("/samples", methods=["GET"])
    @jwt_required()
    def samples():
        start_of_week = get_start_of_week()
        current_samples = (
            db.session.execute(
                db.select(Sample)
                .filter(Sample.email == current_user.email)
                .filter(Sample.date >= start_of_week)
                .order_by(db.desc("date"))
            )
            .scalars()
            .all()
        )
        previous_samples = (
            db.session.execute(
                db.select(Sample)
                .filter(Sample.email == current_user.email)
                .filter(Sample.date < start_of_week)
                .order_by(db.desc("date"))
            )
            .scalars()
            .all()
        )
        return jsonify(
            current_samples=current_samples, previous_samples=previous_samples
        )

    @app.route("/reference_sequence", methods=["POST"])
    @jwt_required()
    def reference_sequence():
        primary_key = request.json.get("primary_key", None)
        logger.info(
            f"User {current_user.email} requesting reference sequence with key {primary_key}"
        )
        filters = {"primary_key": primary_key}
        if not current_user.is_admin:
            filters["email"] = current_user.email
        user_sample = db.session.execute(
            db.select(Sample).filter_by(**filters)
        ).scalar_one_or_none()
        if user_sample is None:
            logger.info(f"  -> sample with key {primary_key} not found")
            return jsonify("Sample not found"), 401
        if user_sample.reference_sequence_description is None:
            logger.info(
                f"  -> sample with key {primary_key} found but does not contain a reference sequence"
            )
            return jsonify("Sample does not contain a reference sequence"), 401
        logger.info(
            f"  -> found reference sequence with description {user_sample.reference_sequence_description}"
        )
        year, week, day = user_sample.date.isocalendar()
        filename = f"{data_path}/{year}/{week}/inputs/references/{user_sample.primary_key}_{user_sample.name}.fasta"
        file = pathlib.Path(filename)
        if not file.is_file():
            logger.info(f"  -> fasta file {file} not found")
            return jsonify("Fasta file not found"), 401
        logger.info(f"Returning fasta file {file}")
        return flask.send_file(file, as_attachment=True)

    @app.route("/result", methods=["POST"])
    @jwt_required()
    def result():
        primary_key = request.json.get("primary_key", None)
        filetype = request.json.get("filetype", None)
        if filetype not in ["fasta", "gbk", "zip"]:
            logger.info(f"  -> invalid filetype {filetype} requested")
            return jsonify(f"Invalid filetype {filetype} requested"), 401
        logger.info(
            f"User {current_user.email} requesting {filetype} results for key {primary_key}"
        )
        filters = {"primary_key": primary_key}
        if not current_user.is_admin:
            filters["email"] = current_user.email
        user_sample = db.session.execute(
            db.select(Sample).filter_by(**filters)
        ).scalar_one_or_none()
        if user_sample is None:
            logger.info(f"  -> sample with key {primary_key} not found")
            return jsonify("Sample not found"), 401
        if (
            (filetype == "fasta" and not user_sample.has_results_fasta)
            or (filetype == "gbk" and not user_sample.has_results_gbk)
            or (filetype == "zip" and not user_sample.has_results_zip)
        ):
            logger.info(
                f"  -> sample with key {primary_key} found but no {filetype} results available"
            )
            return jsonify(f"No {filetype} results available"), 401
        year, week, day = user_sample.date.isocalendar()
        filename = f"{data_path}/{year}/{week}/results/{user_sample.primary_key}_{user_sample.name}.{filetype}"
        file = pathlib.Path(filename)
        if not file.is_file():
            logger.info(f"  -> {filetype} file {file} not found")
            return jsonify(f"Results {filetype} file not found"), 401
        logger.info(f"Returning {filetype} file {file}")
        return flask.send_file(file, as_attachment=True)

    @app.route("/sample", methods=["POST"])
    @jwt_required()
    def add_sample():
        email = current_user.email
        name = request.form.to_dict().get("name", "")
        running_option = request.form.to_dict().get("running_option", "")
        reference_sequence_file = request.files.to_dict().get("file", None)
        logger.info(f"Adding sample {name} from {email}")
        new_sample, error_message = add_new_sample(
            email, name, running_option, reference_sequence_file, data_path
        )
        if new_sample is not None:
            logger.info(f"  - > success")
            return jsonify(sample=new_sample)
        return jsonify(message=error_message), 401

    @app.route("/admin/settings", methods=["GET", "POST"])
    @jwt_required()
    def admin_settings():
        if not current_user.is_admin:
            return jsonify("Admin account required"), 401
        if flask.request.method == "POST":
            message, code = set_current_settings(current_user.email, request.json)
            return jsonify(message=message), code
        else:
            return get_current_settings()

    @app.route("/admin/samples", methods=["GET"])
    @jwt_required()
    def admin_all_samples():
        if not current_user.is_admin:
            return jsonify("Admin account required"), 401
        year, week, day = datetime.date.today().isocalendar()
        start_of_week = datetime.date.fromisocalendar(year, week, 1)
        current_samples = (
            db.session.execute(
                db.select(Sample)
                .filter(Sample.date >= start_of_week)
                .order_by(db.desc("date"))
            )
            .scalars()
            .all()
        )
        previous_samples = (
            db.session.execute(
                db.select(Sample)
                .filter(Sample.date < start_of_week)
                .order_by(db.desc("date"))
            )
            .scalars()
            .all()
        )
        return jsonify(
            current_samples=current_samples, previous_samples=previous_samples
        )

    @app.route("/admin/zipsamples", methods=["POST"])
    @jwt_required()
    def admin_zip_samples():
        if not current_user.is_admin:
            return jsonify("Admin account required"), 401
        logger.info(
            f"Request for zipfile of samples from Admin user {current_user.email}"
        )
        zip_file = update_samples_zipfile(data_path, datetime.date.today())
        return flask.send_file(zip_file, as_attachment=True)

    @app.route("/admin/users", methods=["GET"])
    @jwt_required()
    def admin_users():
        if current_user.is_admin:
            users = db.session.execute(db.select(User)).scalars().all()
            return jsonify(users=[user.as_dict() for user in users])
        return jsonify("Admin account required"), 401

    @app.route("/admin/token", methods=["GET"])
    @jwt_required()
    def admin_token():
        if current_user.is_admin:
            access_token = create_access_token(
                identity=current_user, expires_delta=datetime.timedelta(weeks=52)
            )
            return jsonify(access_token=access_token)
        return jsonify("Admin account required"), 401

    @app.route("/admin/result", methods=["POST"])
    @jwt_required()
    def admin_upload_result():
        if not current_user.is_admin:
            return jsonify("Admin account required"), 401
        email = current_user.email
        zipfile = request.files.to_dict().get("file", None)
        logger.info(f"Results uploaded by {email}")
        message, code = process_result(zipfile, data_path)
        return jsonify(message=message), code

    with app.app_context():
        db.create_all()
        _add_temporary_users_for_testing()
        _add_temporary_samples_for_testing()

    return app
