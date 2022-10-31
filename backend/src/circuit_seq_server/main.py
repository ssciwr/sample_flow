from typing import Optional
import secrets
import argon2
import click

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

from circuit_seq_server.logger import get_logger
from circuit_seq_server.primary_key import get_primary_key

app = Flask("CircuitSeqServer")

app.config["JWT_SECRET_KEY"] = secrets.token_urlsafe(64)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "sqlite:///CircuitSeq.db"  # todo: persist to disk
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # todo: needed or not?

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
    name: str = db.Column(db.String(256), nullable=False)


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


def add_new_sample(email: str, name: str) -> Optional[Sample]:
    count = len(
        db.session.execute(db.select(Sample)).all()
    )  # todo: filter only samples from current week
    week = 1  # todo: calculate week number based on date
    key = get_primary_key(week, count)
    if key is None:
        return None

    new_sample = Sample(email=email, name=name, primary_key=key)
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
    return jsonify(user=current_user.as_dist(), access_token=access_token)


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
    print(user_samples, flush=True)
    return jsonify(samples=user_samples)


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
    name = request.json.get("name", None)
    logger.info(f"Adding sample {name} from {email}")
    new_sample = add_new_sample(email, name)
    if new_sample is not None:
        logger.info(f"  - > success")
        return jsonify(sample=new_sample)
    return jsonify(message="No more samples available this week."), 401


@click.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=5000, show_default=True)
def main(host: str, port: int):
    with app.app_context():
        db.create_all()
        if (
            db.session.execute(
                db.select(User).filter_by(id="admin")
            ).scalar_one_or_none()
            is None
        ):
            print("admin")
            # temporary default admin user for testing purposes
            add_new_user("admin@embl.de", "admin", True)
            # temporary user for testing purposes
            add_new_user("user@embl.de", "user", False)

    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
