from __future__ import annotations
from typing import Optional, Any
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

db = SQLAlchemy()
ph = argon2.PasswordHasher()
logger = get_logger("CircuitSeqServer")

# todo: put these in db? have them modifiable by an admin user (to take effect the following week)?
plate_n_rows = 8
plate_n_cols = 12


@dataclass
class Sample(db.Model):
    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(256), nullable=False)
    primary_key: str = db.Column(db.String(32), nullable=False, unique=True)
    name: str = db.Column(db.String(128), nullable=False)
    reference_sequence_description: Optional[str] = db.Column(
        db.String(256), nullable=True
    )
    date: datetime.date = db.Column(db.Date, nullable=False)


def count_samples_this_week(current_date: Optional[datetime.date] = None) -> int:
    return len(
        db.session.execute(
            db.select(Sample).filter(Sample.date >= get_start_of_week(current_date))
        ).all()
    )


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
    email: str,
    name: str,
    reference_sequence_file: Optional[Any],
    data_path: str,
) -> Optional[Sample]:
    today = datetime.date.today()
    year, week, day = today.isocalendar()
    count = count_samples_this_week(today)
    key = get_primary_key(
        year=year,
        week=week,
        current_count=count,
        n_rows=plate_n_rows,
        n_cols=plate_n_cols,
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
            add_new_user(email, name, is_admin)


def _add_temporary_samples_for_testing():
    # add temporary samples if not already in db
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
                    date=datetime.date.fromisocalendar(2022, week, n),
                )
                db.session.add(new_sample)
                db.session.commit()
