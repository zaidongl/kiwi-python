"""JsonUtils: helpers to read and validate JSON using a simple dot-path syntax.

Path examples:
- "users[0].name"
- "a.b.c"

Also provides simple constructors to load JSON from a string or file.
"""
from typing import Any, Dict, Optional, Tuple, Union
import json

from kiwi.exception.path_error import PathError
from kiwi.exception.validation_error import ValidationError


class JsonUtils:
    @staticmethod
    def _parse_segment(segment: str) -> Tuple[str, Optional[int]]:
        """Parse a segment like 'users[2]' into ('users', 2) or ('key', None)."""
        if "[" in segment and segment.endswith("]"):
            key, idx = segment.split("[", 1)
            try:
                index = int(idx[:-1])
            except ValueError:
                raise PathError(f"Invalid list index in segment '{segment}'")
            return key, index
        return segment, None

    # ------------------ constructors ------------------
    @staticmethod
    def from_string(json_text: str) -> Dict[str, Any]:
        """Parse JSON from a string and return a dict/list payload."""
        try:
            return json.loads(json_text)
        except Exception as e:
            raise ValueError(f"Invalid JSON string provided: {e}")

    @staticmethod
    def from_file(path: str) -> Dict[str, Any]:
        """Read JSON from a file path and return the parsed payload."""
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as e:
            raise ValueError(f"Failed to load JSON from file '{path}': {e}")

    @staticmethod
    def load(source: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Load JSON payload from a string, file path or dict-like object.

        - If `source` is a dict/list, it is returned as-is.
        - If `source` is a string, tries json.loads; if that fails, treats it as a file path.
        """
        if isinstance(source, (dict, list)):
            return source  # type: ignore
        if not isinstance(source, str):
            raise TypeError("source must be a dict, list, or JSON string/file path")

        # try parse as json string first
        try:
            return JsonUtils.from_string(source)
        except ValueError:
            # fall back to file
            return JsonUtils.from_file(source)

    # ------------------ path helpers ------------------
    @staticmethod
    def get(data: Dict[str, Any], path: str) -> Any:
        """Return the value at the dot-path or raise PathError if it doesn't exist."""
        if not path:
            return data

        current: Any = data
        for raw_seg in path.split('.'):
            if raw_seg == "":
                continue
            key, idx = JsonUtils._parse_segment(raw_seg)
            if isinstance(current, dict):
                if key not in current:
                    raise PathError(f"Path '{path}' not found: missing key '{key}'")
                current = current[key]
            else:
                raise PathError(f"Path '{path}' not found: expected dict at segment '{raw_seg}'")

            if idx is not None:
                if not isinstance(current, (list, tuple)):
                    raise PathError(f"Path '{path}' not found: expected list at '{key}'")
                try:
                    current = current[idx]
                except IndexError:
                    raise PathError(f"Path '{path}' not found: index {idx} out of range for '{key}'")

        return current

    @staticmethod
    def exists(data: Dict[str, Any], path: str) -> bool:
        try:
            JsonUtils.get(data, path)
            return True
        except PathError:
            return False

    @staticmethod
    def count(data: Dict[str, Any], path: str) -> int:
        try:
            val = JsonUtils.get(data, path)
        except PathError:
            return 0
        if isinstance(val, (list, tuple)):
            return len(val)
        return 1

    @staticmethod
    def check_type(data: Dict[str, Any], path: str, expected_type: Union[Tuple[type, ...], type]) -> bool:  # type: ignore
        try:
            val = JsonUtils.get(data, path)
        except PathError:
            return False
        if not isinstance(expected_type, tuple):
            expected = (expected_type,)
        else:
            expected = expected_type
        return isinstance(val, expected)

    @staticmethod
    def assert_type(data: Dict[str, Any], path: str, expected_type: Union[Tuple[type, ...], type]) -> None:  # type: ignore
        if not JsonUtils.check_type(data, path, expected_type):
            try:
                val = JsonUtils.get(data, path)
                actual = type(val).__name__
            except PathError:
                raise ValidationError(f"expected type {expected_type} at '{path}' but path was not found")
            raise ValidationError(f"expected type {expected_type} at '{path}' but found {actual}")

    # renamed: check_value -> get_value
    @staticmethod
    def get_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """Return value at path if present, otherwise return `default` (non-raising)."""
        try:
            return JsonUtils.get(data, path)
        except PathError:
            return default

    @staticmethod
    def assert_value(data: Dict[str, Any], path: str, expected_value: Any) -> None:
        # distinguish between missing path and actual None values
        if not JsonUtils.exists(data, path):
            raise ValidationError(f"expected value {expected_value} at '{path}' but path was not found")
        val = JsonUtils.get(data, path)
        if val != expected_value:
            raise ValidationError(f"expected value {expected_value} at '{path}' but found {val}")
