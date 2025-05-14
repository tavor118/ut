from typing import Any, Dict

from pytest import fixture, mark

from ut import nget


class TestNget:
    @fixture
    def test_data(self) -> Dict[str, Any]:
        return {
            "peoples": [
                {
                    "name": "Ivan",
                    "kids": [{"name": "Leo", "age": 7}, {"name": "Ann", "age": 1}],
                },
                {"name": "Juan", "kids": None},
            ]
        }

    @mark.parametrize(
        "keys", [["peoples", 0, "kids", 0, "age"], ["peoples.0.kids.0.age"]]
    )
    def test_key_exists(self, test_data: Dict[str, Any], keys: list) -> None:
        expected_result = 7
        result = nget(test_data, *keys)
        assert result == expected_result

    @mark.parametrize("keys", [["foo", "bar", 999], ["foo.bar.999"]])
    def test_missing_key(self, test_data: Dict[str, Any], keys: list) -> None:
        result = nget(test_data, *keys)
        assert result is None

    @mark.parametrize("keys", [["peoples", 999, "foo"], ["peoples.999.foo"]])
    def test_missing_index(self, test_data: Dict[str, Any], keys: list) -> None:
        result = nget(test_data, *keys)
        assert result is None

    @mark.parametrize("keys", [["peoples", 1, "foo"], ["peoples.1.foo"]])
    def test_default(self, test_data: Dict[str, Any], keys: list) -> None:
        default = "Mary"
        result = nget(test_data, *keys, default=default)
        assert result == default

    def test_no_items(self, test_data: Dict[str, Any]) -> None:
        assert nget(test_data) == test_data

    def test_empty_container(self) -> None:
        assert nget({}, "any", "keys") is None
        assert nget([], 0, 1) is None
