import pytest

from kiwi.utils.json_utils import JsonUtils
from kiwi.exception.path_error import PathError
from kiwi.exception.validation_error import ValidationError


def test_get_and_exists_basic():
    data = {"a": {"b": [{"c": 1}]}}
    assert JsonUtils.exists(data, "a.b[0].c")
    assert JsonUtils.get(data, "a.b[0].c") == 1


def test_get_missing():
    data = {"a": {"b": [{"c": 1}]}}
    assert not JsonUtils.exists(data, "a.x")
    with pytest.raises(PathError):
        JsonUtils.get(data, "a.x")


def test_count_and_type_asserts():
    data = {"a": {"b": [{"c": 1}, {"c": 2}]}}
    assert JsonUtils.count(data, "a.b") == 2
    assert JsonUtils.check_type(data, "a.b[0].c", int)
    JsonUtils.assert_type(data, "a.b[0].c", int)
    with pytest.raises(ValidationError):
        JsonUtils.assert_type(data, "a.b[0].c", str)


def test_value_asserts_and_get_value():
    data = {"a": {"b": [{"c": 1}]}}
    assert JsonUtils.get_value(data, "a.b[0].c", None) == 1
    JsonUtils.assert_value(data, "a.b[0].c", 1)
    with pytest.raises(ValidationError):
        JsonUtils.assert_value(data, "a.b[0].c", 2)


def test_constructors(tmp_path):
    # from_string
    json_text = '{"x": 10}'
    payload = JsonUtils.from_string(json_text)
    assert payload["x"] == 10

    # from_file and load
    p = tmp_path / "t.json"
    p.write_text(json_text, encoding="utf-8")
    payload2 = JsonUtils.from_file(str(p))
    assert payload2["x"] == 10
    # load from dict
    assert JsonUtils.load(payload2)["x"] == 10
    # load from string (json content)
    assert JsonUtils.load(json_text)["x"] == 10
    # load from file path
    assert JsonUtils.load(str(p))["x"] == 10


def test_add_value():
    data = {"a": {"b": []}}
    JsonUtils.add_value(data, "a.b[0].c", 42)
    assert data == {"a": {"b": [{"c": 42}]}}

    # Add to existing dict
    JsonUtils.add_value(data, "a.d", "new")
    assert data["a"]["d"] == "new"

    # Create intermediates
    JsonUtils.add_value(data, "x.y.z", 100)
    assert data["x"]["y"]["z"] == 100


def test_update_value():
    data = {"a": {"b": [{"c": 1}]}}
    JsonUtils.update_value(data, "a.b[0].c", 99)
    assert data["a"]["b"][0]["c"] == 99

    # Update non-existing should raise
    with pytest.raises(PathError):
        JsonUtils.update_value(data, "a.missing", 123)


def test_remove_value():
    data = {"a": {"b": [{"c": 1}, {"d": 2}], "e": 3}}
    JsonUtils.remove_value(data, "a.b[0].c")
    assert data == {"a": {"b": [{}, {"d": 2}], "e": 3}}

    JsonUtils.remove_value(data, "a.e")
    assert data == {"a": {"b": [{}, {"d": 2}]}}

    # Remove non-existing should raise
    with pytest.raises(PathError):
        JsonUtils.remove_value(data, "a.missing")

    # Remove from list
    JsonUtils.remove_value(data, "a.b[1]")
    assert data == {"a": {"b": [{}]}}
