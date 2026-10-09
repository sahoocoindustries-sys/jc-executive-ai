"""Tests for JC agent plan parsing and safety validation."""

import pytest

from jc.core.agent_planner import parse_plan_response


def test_parse_plan_response_accepts_valid_json_and_normalizes_steps():
    raw = '''{"title":"Launch a landing page","summary":"Create and verify a simple page.","steps":[{"title":"Research","agent":"research","description":"Collect requirements."},{"title":"Build","agent":"developer","description":"Create the page."}]}'''

    plan = parse_plan_response(raw)

    assert plan["title"] == "Launch a landing page"
    assert len(plan["steps"]) == 2
    assert plan["steps"][0]["agent"] == "research"
    assert all(step["status"] == "pending_approval" for step in plan["steps"])


def test_parse_plan_response_accepts_json_fenced_in_markdown():
    raw = '''```json\n{"title":"Research market","summary":"Assess demand.","steps":[{"title":"Find sources","agent":"research","description":"Find credible sources."}]}\n```'''

    assert parse_plan_response(raw)["title"] == "Research market"


def test_parse_plan_response_rejects_non_json_and_empty_steps():
    with pytest.raises(ValueError, match="valid JSON"):
        parse_plan_response("I will do this task now.")

    with pytest.raises(ValueError, match="at least one step"):
        parse_plan_response('{"title":"No steps","summary":"Empty","steps":[]}')


def test_parse_plan_response_limits_steps_and_requires_safe_fields():
    too_many = {"title": "Plan", "summary": "Summary", "steps": [
        {"title": f"Step {i}", "agent": "research", "description": "Do research."}
        for i in range(9)
    ]}
    import json

    with pytest.raises(ValueError, match="8 steps"):
        parse_plan_response(json.dumps(too_many))

    with pytest.raises(ValueError, match="description"):
        parse_plan_response('{"title":"Plan","summary":"Summary","steps":[{"title":"Step","agent":"research"}]}')
