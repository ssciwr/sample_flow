from flask_sqlalchemy import SQLAlchemy
import argon2
from circuit_seq_server.model import User, Sample
import datetime


def add_test_users(app):
    db = SQLAlchemy(app)
    ph = argon2.PasswordHasher()
    with app.app_context():
        # add users for tests
        for (name, is_admin) in [("admin", True), ("user", False)]:
            email = f"{name}@embl.de"
            db.session.add(
                User(
                    email=email,
                    password_hash=ph.hash(name),
                    activated=True,
                    is_admin=is_admin,
                )
            )
            db.session.commit()


def add_test_samples(app):
    db = SQLAlchemy(app)
    with app.app_context():
        # add samples for tests
        week = 46
        for n, name in zip(
            [1, 2, 3, 4],
            [
                "no_ref_seq",
                "ZIP_TEST_pMC_Final_Kan",
                "ZIP_TEST_pCW571",
                "ZIP_TEST_pDONR_amilCP",
            ],
        ):
            key = f"22_{week}_A{n}"
            new_sample = Sample(
                email="user@embl.de",
                name=name,
                primary_key=key,
                reference_sequence_description=None,
                running_option="running_option",
                date=datetime.date.fromisocalendar(2022, week, n),
                has_results_zip=False,
                has_results_fasta=False,
                has_results_gbk=False,
            )
            db.session.add(new_sample)
            db.session.commit()
