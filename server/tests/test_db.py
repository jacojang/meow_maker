import sys

from app.db import connect, ensure_initialized, init_db


def test_init_db_creates_the_parent_directory(tmp_path):
    db_path = str(tmp_path / "nested" / "meow_maker.db")

    init_db(db_path)

    assert (tmp_path / "nested" / "meow_maker.db").exists()


def test_init_db_is_idempotent(tmp_path):
    db_path = str(tmp_path / "meow_maker.db")

    init_db(db_path)
    init_db(db_path)  # must not raise on the second call

    with connect(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }

    assert {"player", "game"} <= tables


def test_ensure_initialized_creates_the_db_on_first_call(tmp_path):
    db_path = str(tmp_path / "lazy.db")
    assert not (tmp_path / "lazy.db").exists()

    ensure_initialized(db_path)

    assert (tmp_path / "lazy.db").exists()


def test_ensure_initialized_does_not_error_on_repeated_calls(tmp_path):
    db_path = str(tmp_path / "lazy.db")

    ensure_initialized(db_path)
    ensure_initialized(db_path)  # must not raise


def test_importing_the_app_does_not_touch_disk(tmp_path, monkeypatch):
    monkeypatch.setenv("MEOW_DB_PATH", str(tmp_path / "should-not-exist.db"))
    monkeypatch.delitem(sys.modules, "app.main", raising=False)

    import app.main  # noqa: F401

    assert not (tmp_path / "should-not-exist.db").exists()
