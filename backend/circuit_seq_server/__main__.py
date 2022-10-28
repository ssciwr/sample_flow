from typing import Optional
import math
import secrets
import argon2
import logging
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


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(name)s  | [%(asctime)s %(levelname)s] %(message)s", "%H:%M:%S"
        )
    )
    logger.addHandler(handler)
    return logger


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


def add_new_user(email: str, password: str) -> bool:
    # todo: active should be false until they click on emailed activation link
    db.session.add(User(email=email, password_hash=ph.hash(password), activated=True))
    db.session.commit()
    return True


def add_new_sample(email: str, name: str) -> Optional[Sample]:
    n_rows = 8
    n_cols = 12
    max_samples = n_rows * n_cols
    week = 1  # todo: calculate this from current date
    row_labels = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
    ]
    count = len(
        db.session.execute(db.select(Sample)).all()
    )  # todo: filter only samples from current week
    if count >= max_samples:
        return None

    i_row = math.floor(count / n_cols)
    i_col = count % n_cols
    key = f"{week}_{row_labels[i_row]}{i_col + 1}"
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
    return jsonify(access_token=access_token)


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


@app.route("/whoami", methods=["GET"])
@jwt_required()
def whoami():
    print(current_user, flush=True)
    # We can now access our sqlalchemy User object via `current_user`.
    return jsonify(id=current_user.id, email=current_user.email)


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
    # todo: should only be accessible to admin users
    all_user_samples = db.session.execute(db.select(Sample)).scalars().all()
    return jsonify(samples=all_user_samples)


@app.route("/allusers", methods=["GET"])
@jwt_required()
def all_users():
    # todo: should only be accessible to admin users
    users = db.session.execute(db.select(User)).scalars().all()
    return jsonify(
        users=[
            {"id": user.id, "email": user.email, "activated": user.activated}
            for user in users
        ]
    )


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
@click.option('--host', default='127.0.0.1', show_default=True)
@click.option('--port', default=5000, show_default=True)
def main(host:str, port:int):
    with app.app_context():
        db.create_all()

    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
