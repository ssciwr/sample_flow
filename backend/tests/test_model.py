import circuit_seq_server.model as model
import datetime


def test_add_new_sample(app, tmp_path):
    with app.app_context():
        year, week, day = datetime.date.today().isocalendar()
        current_date = datetime.date.fromisocalendar(year, week, day)
        this_week_samples = model.db.select(model.Sample).filter(
            model.Sample.date >= current_date
        )
        assert len(model.db.session.execute(this_week_samples).scalars().all()) == 0
        assert model.count_samples_this_week() == 0
        # add a sample without a reference sequence
        new_sample = model.add_new_sample("u1@embl.de", "s1", None, str(tmp_path))
        assert new_sample is not None
        assert new_sample.email == "u1@embl.de"
        assert new_sample.name == "s1"
        assert new_sample.primary_key == f"{year%100}_{week}_A1"
        assert new_sample.date == current_date
        assert new_sample.reference_sequence_description is None
        samples = model.db.session.execute(this_week_samples).scalars().all()
        assert len(samples) == 1
        assert samples[0] == new_sample
        assert model.count_samples_this_week() == 1


def test_add_new_user(app):
    with app.app_context():
        n_users = len(
            model.db.session.execute(model.db.select(model.User)).scalars().all()
        )
        # add a new user
        email = "x@embl.de"
        password = "passwdP1"
        assert model.add_new_user(email, password, is_admin=False) is True
        assert (
            len(model.db.session.execute(model.db.select(model.User)).scalars().all())
            == n_users + 1
        )
        user = model.db.session.execute(
            model.db.select(model.User).filter(model.User.email == email)
        ).scalar_one_or_none()
        assert user is not None
        assert user.email == email
        assert user.is_admin is False
        # check password
        assert user.check_password("wrong") is False
        assert user.check_password(password) is True
        # set new password
        assert user.set_password("wrong", "new") is False
        assert user.check_password(password) is True
        assert user.set_password(password, "newPassword2") is True
        # check new password
        assert user.check_password(password) is False
        assert user.check_password("newPassword2") is True
