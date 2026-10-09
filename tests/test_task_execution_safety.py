"""Tests that incomplete task execution is never reported as successful."""

import asyncio

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from jc.api.routes.tasks import TaskUpdate, execute_task
from jc.database.models import TaskModel


class FakeQuery:
    def __init__(self, task):
        self.task = task

    def filter(self, _expression):
        return self

    def first(self):
        return self.task


class FakeDB:
    def __init__(self, task):
        self.task = task

    def query(self, model):
        assert model is TaskModel
        return FakeQuery(self.task)


def test_execute_endpoint_refuses_to_claim_unimplemented_execution():
    task = type("Task", (), {"id": "task-1", "status": "pending_approval"})()

    with pytest.raises(HTTPException) as raised:
        asyncio.run(execute_task("task-1", FakeDB(task)))

    assert raised.value.status_code == 501
    assert "no external action was performed" in raised.value.detail
    assert task.status == "pending_approval"


def test_task_update_cannot_manually_mark_work_as_executing_or_completed():
    with pytest.raises(ValidationError):
        TaskUpdate(status="executing")
    with pytest.raises(ValidationError):
        TaskUpdate(status="completed")
