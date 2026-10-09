"""Regression tests for SQLAlchemy's reserved metadata attribute name."""

from jc.database.models import BackupModel, MessageModel, SessionModel


def test_session_metadata_column_uses_safe_python_attribute_name():
    assert "metadata" in SessionModel.__table__.columns
    assert hasattr(SessionModel, "metadata_json")


def test_message_metadata_column_uses_safe_python_attribute_name():
    assert "metadata" in MessageModel.__table__.columns
    assert hasattr(MessageModel, "metadata_json")


def test_backup_metadata_column_uses_safe_python_attribute_name():
    assert "metadata" in BackupModel.__table__.columns
    assert hasattr(BackupModel, "metadata_json")
