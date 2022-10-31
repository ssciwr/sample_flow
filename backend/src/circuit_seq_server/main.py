from __future__ import annotations
from typing import Optional, Any
import secrets
import argon2
import click
import tempfile
import pathlib

import flask
from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import create_access_token
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from flask_cors import CORS
from dataclasses import dataclass

from Bio import SeqIO

from circuit_seq_server.logger import get_logger
from circuit_seq_server.primary_key import get_primary_key

app = Flask("CircuitSeqServer")

app.config["JWT_SECRET_KEY"] = secrets.token_urlsafe(64)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///CircuitSeq.db"  # todo: persist to disk
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 64 * 1000 * 1000  # 64mb max file upload

CORS(app)  # todo: limit ports / routes

jwt = JWTManager(app)
db = SQLAlchemy(app)
ph = argon2.PasswordHasher()
logger = get_logger("CircuitSeqServer")


@dataclass
class Sample(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(256), nullable=False)
    primary_key: str = db.Column(db.String(32), nullable=False, unique=True)
    name: str = db.Column(db.String(128), nullable=False)
    reference_sequence_description: str = db.Column(db.String(256), nullable=True)


@dataclass
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    activated = db.Column(db.Boolean, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)

    def set_password(self, old_password: str, new_password: str) -> bool:
        if self.check_password(old_password):
            self.password_hash = ph.hash(new_password)
            db.session.commit()
            return True
        return False

    def check_password(self, password: str) -> bool:
        try:
            ph.verify(self.password_hash, password)
        except argon2.exceptions.VerificationError:
            return False
        if ph.check_needs_rehash(self.password_hash):
            self.password_hash = ph.hash(password)
            db.session.commit()
        return True

    def as_dict(self, include_password_hash: bool = False):
        user_as_dict = {
            "id": self.id,
            "email": self.email,
            "activated": self.activated,
            "is_admin": self.is_admin,
        }
        if include_password_hash:
            user_as_dict["password_hash"] = self.password_hash
        return user_as_dict


def add_new_user(email: str, password: str, is_admin: bool = False) -> bool:
    # todo: active should be false until they click on emailed activation link
    db.session.add(
        User(
            email=email,
            password_hash=ph.hash(password),
            activated=True,
            is_admin=is_admin,
        )
    )
    db.session.commit()
    return True


def add_new_sample(
    email: str, name: str, reference_sequence_file: Optional[Any]
) -> Optional[Sample]:
    count = len(
        db.session.execute(db.select(Sample)).all()
    )  # todo: filter only samples from current week
    week = 1  # todo: calculate week number based on date
    key = get_primary_key(week, count)
    if key is None:
        return None
    reference_sequence_description: Optional[str] = None
    if reference_sequence_file is not None:
        filename = f"{key}_{name}.fasta"
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_file = pathlib.Path(tmp_dir) / filename
            logger.info(
                f"Saving {reference_sequence_file} to temporary file {temp_file}"
            )
            reference_sequence_file.save(temp_file)
            try:
                logger.info(f"Parsing fasta file")
                record = next(SeqIO.parse(temp_file, "fasta").records)
                logger.info(record.id)
                logger.info(record.description)
                logger.info(record.format("fasta"))
                logger.info(f"Writing fasta file to {filename}")
                SeqIO.write(record, filename, "fasta")
                reference_sequence_description = record.description
            except Exception as e:
                logger.info(f"Failed to parse fasta file: {e}")

    new_sample = Sample(
        email=email,
        name=name,
        primary_key=key,
        reference_sequence_description=reference_sequence_description,
    )
    db.session.add(new_sample)
    db.session.commit()
    return new_sample


# https://flask-jwt-extended.readthedocs.io/en/stable/api/#flask_jwt_extended.JWTManager.user_identity_loader
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


# https://flask-jwt-extended.readthedocs.io/en/stable/api/#flask_jwt_extended.JWTManager.user_lookup_loader
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.session.execute(
        db.select(User).filter_by(id=identity)
    ).scalar_one_or_none()


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    logger.info(f"Login request from {email}")
    user = db.session.execute(
        db.select(User).filter_by(email=email)
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
    if add_new_user(email, password):
        logger.info(f"  -> signup successful")
        logger.info(f"  -> [todo] activation email sent")
        return jsonify(result="success")
    return jsonify(result="Signup failed"), 401


@app.route("/remaining", methods=["GET"])
def remaining():
    # todo: calculate this properly: correct max number, filter samples for this week
    return jsonify(remaining=96 - len(db.session.execute(db.select(Sample)).all()))


@app.route("/samples", methods=["GET"])
@jwt_required()
def samples():
    user_samples = (
        db.session.execute(db.select(Sample).filter_by(email=current_user.email))
        .scalars()
        .all()
    )
    return jsonify(samples=user_samples)


@app.route("/reference_sequence", methods=["POST"])
@jwt_required()
def reference_sequence():
    primary_key = request.json.get("primary_key", None)
    logger.info(
        f"User {current_user.email} requesting reference sequence with key {primary_key}"
    )
    filters = {"primary_key": primary_key}
    if not current_user.is_admin:
        filters["email"]=current_user.email
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
    file = pathlib.Path(f"{user_sample.primary_key}_{user_sample.name}.fasta")
    if not file.is_file():
        logger.info(f"  -> fasta file {file} not found")
        return jsonify("Fasta file not found"), 401
    logger.info(f"Returning fasta file {file}")
    return flask.send_file(file, as_attachment=True)


@app.route("/allsamples", methods=["GET"])
@jwt_required()
def all_samples():
    if current_user.is_admin:
        all_user_samples = db.session.execute(db.select(Sample)).scalars().all()
        return jsonify(samples=all_user_samples)
    return jsonify("Admin account required"), 401


@app.route("/allusers", methods=["GET"])
@jwt_required()
def all_users():
    if current_user.is_admin:
        users = db.session.execute(db.select(User)).scalars().all()
        return jsonify(users=[user.as_dict() for user in users])
    return jsonify("Admin account required"), 401


@app.route("/addsample", methods=["POST"])
@jwt_required()
def add_sample():
    email = current_user.email
    name = request.form.to_dict().get("name", "")
    reference_sequence_file = request.files.to_dict().get("file", None)
    logger.info(f"Adding sample {name} from {email}")
    new_sample = add_new_sample(email, name, reference_sequence_file)
    if new_sample is not None:
        logger.info(f"  - > success")
        return jsonify(sample=new_sample)
    return jsonify(message="No more samples available this week."), 401


def _add_temporary_users_for_testing():
    # add temporary testing users if not already in db
    for (name, is_admin) in [("admin", True), ("user", False)]:
        email = f"{name}@embl.de"
        if not db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none():
            add_new_user(email, name, is_admin)


@click.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=5000, show_default=True)
def main(host: str, port: int):
    with app.app_context():
        db.create_all()
        _add_temporary_users_for_testing()

    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
