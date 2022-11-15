from __future__ import annotations
from typing import Optional, Any, Dict, Tuple
import re
import shutil
import argon2
import tempfile
import pathlib
import datetime
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from Bio import SeqIO
from circuit_seq_server.logger import get_logger
from circuit_seq_server.primary_key import get_primary_key
from circuit_seq_server.date_utils import get_start_of_week
import csv

db = SQLAlchemy()
ph = argon2.PasswordHasher()
logger = get_logger("CircuitSeqServer")


@dataclass
class Settings(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    datetime: datetime.datetime = db.Column(db.DateTime, nullable=False)
    email: str = db.Column(db.String(256), nullable=False)
    settings_dict: Dict = db.Column(db.PickleType, nullable=False)


def default_settings_dict() -> Dict:
    return {
        "plate_n_rows": 8,
        "plate_n_cols": 12,
        "running_options": ["dna_r9.4.1_450bps_sup.cfg", "dna_r9.4.1_480bps_sup.cfg"],
    }


def get_current_settings() -> Dict:
    settings_tuple = db.session.execute(
        db.select(Settings).order_by(db.desc(Settings.id))
    ).first()
    if settings_tuple is not None:
        return settings_tuple[0].settings_dict
    # no settings in db: create default settings and add to db
    settings = Settings(
        datetime=datetime.datetime.today(),
        email="default",
        settings_dict=default_settings_dict(),
    )
    db.session.add(settings)
    db.session.commit()
    return settings.settings_dict


def set_current_settings(email: str, settings_dict: Dict) -> Tuple[str, int]:
    for required_field in default_settings_dict():
        if required_field not in settings_dict:
            return (
                f"Required field {required_field} missing - settings not updated",
                401,
            )
    settings = Settings(
        datetime=datetime.datetime.today(), email=email, settings_dict=settings_dict
    )
    db.session.add(settings)
    db.session.commit()
    return f"Settings updated by {settings.email} at {settings.datetime}", 200


@dataclass
class Sample(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(256), nullable=False)
    primary_key: str = db.Column(db.String(32), nullable=False, unique=True)
    name: str = db.Column(db.String(128), nullable=False)
    running_option: str = db.Column(db.String(128), nullable=False)
    reference_sequence_description: Optional[str] = db.Column(
        db.String(256), nullable=True
    )
    date: datetime.date = db.Column(db.Date, nullable=False)


def _samples_this_week(current_date: Optional[datetime.date] = None):
    start_of_week = get_start_of_week(current_date)
    return db.session.execute(
        db.select(Sample)
        .filter(Sample.date >= start_of_week)
        .filter(Sample.date < start_of_week + datetime.timedelta(weeks=1))
    ).all()


def count_samples_this_week(current_date: Optional[datetime.date] = None) -> int:
    return len(_samples_this_week(current_date))


def _write_samples_as_tsv_this_week(
    data_path: str, current_date: Optional[datetime.date] = None
) -> str:
    current_samples = _samples_this_week(current_date)
    logger.info(current_samples)
    if current_date is None:
        current_date = datetime.date.today()
    year, week, day = current_date.isocalendar()
    filename = f"{data_path}/{year}/{week}/reference/samples.tsv"
    logger.info(f"Updating {filename}...")
    with open(filename, "w", newline="") as tsv_file:
        writer = csv.writer(tsv_file, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "date",
                "primary_key",
                "email",
                "name",
                "running_option",
            ]
        )
        for sample_tuple in current_samples:
            sample = sample_tuple[0]
            logger.info(f"  - {sample.primary_key}")
            writer.writerow(
                [
                    sample.date,
                    sample.primary_key,
                    sample.email,
                    sample.name,
                    sample.running_option,
                ]
            )
    return filename


def update_samples_zipfile(
    data_path: str, current_date: Optional[datetime.date] = None
) -> str:
    year, week, day = datetime.date.today().isocalendar()
    base_path = pathlib.Path(f"{data_path}/{year}/{week}")
    pathlib.Path(f"{base_path}/reference").mkdir(parents=True, exist_ok=True)
    tsv_file = _write_samples_as_tsv_this_week(data_path, current_date)
    logger.info(f"  -> {tsv_file}")
    logger.info(f"Creating zip file of {base_path}/reference..")
    zip_filename = shutil.make_archive(
        str(base_path / "samples"), "zip", base_path / "reference"
    )
    logger.info(f"  -> created zip file {zip_filename}")
    return zip_filename


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

    def as_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "activated": self.activated,
            "is_admin": self.is_admin,
        }


def is_valid_email(email: str) -> bool:
    return re.match(r"\S+@((\S*heidelberg)|embl|dkfz)\.de$", email) is not None


def is_valid_password(password: str) -> bool:
    return re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$", password) is not None


def add_new_user(
    email: str, password: str, is_admin: bool = False, skip_validation: bool = False
) -> Tuple[str, int]:
    if not skip_validation:
        # todo: remove this option when _add_temporary_users_for_testing() is removed
        if not is_valid_email(email):
            return "Please use a uni-heidelberg, dkfz or embl email address.", 401
        if not is_valid_password(password):
            return (
                "Password must contain at least 8 characters, including lower-case, upper-case and a number",
                401,
            )
    # todo: check user doesn't already exist
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
    return (
        f"Successful signup for {email} [todo: please click on the activation link sent to this email address]",
        200,
    )


def add_new_sample(
    email: str,
    name: str,
    running_option: str,
    reference_sequence_file: Optional[Any],
    data_path: str,
) -> Optional[Sample]:
    today = datetime.date.today()
    year, week, day = today.isocalendar()
    count = count_samples_this_week(today)
    settings = get_current_settings()
    key = get_primary_key(
        year=year,
        week=week,
        current_count=count,
        n_rows=settings["plate_n_rows"],
        n_cols=settings["plate_n_cols"],
    )
    if key is None:
        return None
    reference_sequence_description: Optional[str] = None
    pathlib.Path(f"{data_path}/{year}/{week}/reference").mkdir(
        parents=True, exist_ok=True
    )
    if reference_sequence_file is not None:
        filename = f"{data_path}/{year}/{week}/reference/{key}_{name}.fasta"
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_file = pathlib.Path(tmp_dir) / "temp.fasta"
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
        running_option=running_option,
        date=today,
    )
    db.session.add(new_sample)
    db.session.commit()
    return new_sample


def _add_temporary_users_for_testing():
    # add temporary testing users if not already in db
    for (name, is_admin) in [("admin", True), ("user", False)]:
        email = f"{name}@embl.de"
        if not db.session.execute(
            db.select(User).filter(User.email == email)
        ).scalar_one_or_none():
            add_new_user(email, name, is_admin, skip_validation=True)


def _add_temporary_samples_for_testing():
    # add temporary samples if not already in db
    running_option = get_current_settings()["running_options"][0]
    for week in [43, 42, 40]:
        for n in [1, 2, 3]:
            key = f"22_{week}_A{n}"
            if not db.session.execute(
                db.select(Sample).filter(Sample.primary_key == key)
            ).scalar_one_or_none():
                new_sample = Sample(
                    email="user@embl.de",
                    name=f"builtin_test_sample{n}",
                    primary_key=key,
                    reference_sequence_description=None,
                    running_option=running_option,
                    date=datetime.date.fromisocalendar(2022, week, n),
                )
                db.session.add(new_sample)
                db.session.commit()
