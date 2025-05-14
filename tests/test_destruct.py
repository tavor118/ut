import inspect
import re
from typing import Any, Dict
from unittest.mock import Mock

from pytest import fixture, mark, raises

from ut import destruct
from ut.destruct import DestructError


class TestDestruct:
    @fixture
    def test_data(self) -> Dict[str, Any]:
        return {"name": "John", "age": 30, "city": "New York"}

    @mark.parametrize("use_keys", [True, False])
    def test_success(self, test_data: Dict[str, Any], use_keys: bool):
        if use_keys:
            name, age, city = destruct(test_data, keys=["name", "age", "city"])
        else:
            name, age, city = destruct(test_data)

        assert name == "John"
        assert age == 30
        assert city == "New York"

    @mark.parametrize("use_keys", [True, False])
    def test_success_one_key(self, test_data: Dict[str, Any], use_keys: bool):
        city = destruct(test_data, keys=["city"]) if use_keys else destruct(test_data)

        assert city == "New York"

    @mark.parametrize("use_keys", [True, False])
    def test_missing_key(self, test_data: Dict[str, Any], use_keys: bool):
        err_msg = re.escape("Key(s) ['first_name', 'last_name'] not found in dictionary.")
        with raises(KeyError, match=err_msg):
            if use_keys:
                first_name, last_name = destruct(
                    test_data, keys=["first_name", "last_name"]
                )
            else:
                first_name, last_name = destruct(test_data)

    @mark.parametrize("use_keys", [True, False])
    def test_empty_dict(self, use_keys: bool):
        data = {}
        err_msg = re.escape("Key(s) ['name'] not found in dictionary.")
        with raises(KeyError, match=err_msg):
            name = destruct(data, keys=["name"]) if use_keys else destruct(data)
            # if use_keys:
            #     name = destruct(data, keys=["name"])
            # else:
            #     name = destruct(data)

    @mark.parametrize("use_keys", [True, False])
    def test_with_defaults(self, test_data: Dict[str, Any], use_keys: bool):
        if use_keys:
            name, age, country = destruct(
                test_data, keys=["name", "age", "country"], default="N/A"
            )
        else:
            name, age, country = destruct(test_data, default="N/A")

        assert name == "John"
        assert age == 30
        assert country == "N/A"  # Missing key, default value used

    def test_function_call(self):
        def inner_function():
            data = {"x": 10, "y": 20}
            x, y = destruct(data)
            return x, y

        x, y = inner_function()
        assert x == 10
        assert y == 20

    def test_nested_destructuring(self):
        def outer_function():
            data = {"a": 1, "b": 2}

            def inner_function():
                inner_data = {"c": 3, "d": 4}
                c, d = destruct(inner_data)
                return c, d

            a, b = destruct(data)
            c, d = inner_function()
            return a, b, c, d

        a, b, c, d = outer_function()
        assert (a, b, c, d) == (1, 2, 3, 4)


class TestGetVarNames:
    @fixture
    def test_data(self) -> Dict[str, Any]:
        return {"name": "John"}

    def test_no_frame(self, monkeypatch, test_data: Dict[str, Any]):
        monkeypatch.setattr(inspect, "currentframe", Mock(return_value=None))

        err_msg = "Failed to access a frame."
        with raises(DestructError, match=err_msg):
            destruct(test_data)

    def test_no_caller_frame(self, monkeypatch, test_data: Dict[str, Any]):
        mock_frame = Mock()
        mock_frame.f_back = None
        monkeypatch.setattr(inspect, "currentframe", Mock(return_value=mock_frame))

        err_msg = "Failed to access caller's frame."
        with raises(DestructError, match=err_msg):
            destruct(test_data)

    def test_no_code_context(self, monkeypatch, test_data: Dict[str, Any]):
        mock_frame = Mock()
        mock_frame.f_back = Mock()
        mock_frame.f_back.code_context = None
        monkeypatch.setattr(inspect, "currentframe", Mock(return_value=mock_frame))
        monkeypatch.setattr(
            inspect, "getframeinfo", Mock(return_value=Mock(code_context=None))
        )

        err_msg = "Failed to retrieve code context."
        with raises(DestructError, match=err_msg):
            destruct(test_data)

    def test_no_assignment_statement_found(self, test_data: Dict[str, Any]):
        err_msg = "Assignment statement was not found."
        with raises(DestructError, match=err_msg):
            destruct(test_data)
