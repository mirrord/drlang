"""Tests for interpret_dict drop_empty feature."""

from drlang import interpret_dict, DRLConfig


class TestDropEmpty:
    """Test drop_empty configuration option."""

    def test_drop_empty_false_default(self):
        """Test that None values are kept by default."""
        expressions = {
            "present": "$value",
            "missing": "$[missing]",
            "another": "$data",
        }
        context = {"value": "hello", "data": 42}

        result = interpret_dict(expressions, context)

        assert result == {
            "present": "hello",
            "missing": None,  # None is kept
            "another": 42,
        }

    def test_drop_empty_false_explicit(self):
        """Test that None values are kept when drop_empty=False."""
        expressions = {
            "present": "$value",
            "missing": "$[missing]",
            "another": "$data",
        }
        context = {"value": "hello", "data": 42}
        config = DRLConfig(drop_empty=False)

        result = interpret_dict(expressions, context, config)

        assert result == {
            "present": "hello",
            "missing": None,  # None is kept
            "another": 42,
        }

    def test_drop_empty_true(self):
        """Test that None values are excluded when drop_empty=True."""
        expressions = {
            "present": "$value",
            "missing": "$[missing]",
            "another": "$data",
        }
        context = {"value": "hello", "data": 42}
        config = DRLConfig(drop_empty=True)

        result = interpret_dict(expressions, context, config)

        assert result == {
            "present": "hello",
            "another": 42,
            # "missing" is excluded because it's None
        }
        assert "missing" not in result

    def test_drop_empty_with_multiple_none_values(self):
        """Test drop_empty with multiple None values."""
        expressions = {
            "key1": "$[missing1]",
            "key2": "$value",
            "key3": "$[missing2]",
            "key4": "$[missing3]",
            "key5": "$data",
        }
        context = {"value": "test", "data": 100}
        config = DRLConfig(drop_empty=True)

        result = interpret_dict(expressions, context, config)

        assert result == {
            "key2": "test",
            "key5": 100,
        }
        assert len(result) == 2

    def test_drop_empty_with_falsy_values(self):
        """Test that falsy values (0, False, empty string) are NOT dropped."""
        expressions = {
            "zero": "$zero",
            "false": "$false",
            "empty": "$empty",
            "none": "$[missing]",
            "real": "$real",
        }
        context = {
            "zero": 0,
            "false": False,
            "empty": "",
            "real": "value",
        }
        config = DRLConfig(drop_empty=True)

        result = interpret_dict(expressions, context, config)

        # Only None should be dropped, not other falsy values
        assert result == {
            "zero": 0,
            "false": False,
            "empty": "",
            "real": "value",
        }
        assert "none" not in result

    def test_drop_empty_with_nested_dict(self):
        """Test drop_empty with nested dictionaries."""
        expressions = {
            "level1": {
                "present": "$value",
                "missing": "$[missing]",
                "nested": {
                    "deep": "$data",
                    "absent": "$[absent]",
                },
            }
        }
        context = {"value": "hello", "data": 42}
        config = DRLConfig(drop_empty=True)

        result = interpret_dict(expressions, context, config)

        # Nested dict should also have None values dropped
        assert result == {
            "level1": {
                "present": "hello",
                "nested": {
                    "deep": 42,
                },
            }
        }
        assert "missing" not in result["level1"]
        assert "absent" not in result["level1"]["nested"]

    def test_drop_empty_with_lists(self):
        """Test drop_empty with list expressions."""
        expressions = {
            "list1": ["$value", "$[missing]", "$data"],
            "list2": "$[missing]",
            "scalar": "$value",
        }
        context = {"value": "hello", "data": 42}
        config = DRLConfig(drop_empty=True)

        result = interpret_dict(expressions, context, config)

        # Lists themselves are kept, None values inside lists are kept
        # Only top-level keys with None are dropped
        assert result == {
            "list1": ["hello", None, 42],  # List with None is kept
            "scalar": "hello",
        }
        assert "list2" not in result  # This key is dropped because value is None

    def test_drop_empty_all_none(self):
        """Test drop_empty when all values are None."""
        expressions = {
            "missing1": "$[missing1]",
            "missing2": "$[missing2]",
            "missing3": "$[missing3]",
        }
        context = {}
        config = DRLConfig(drop_empty=True)

        result = interpret_dict(expressions, context, config)

        assert result == {}
        assert len(result) == 0

    def test_drop_empty_with_conditional_none(self):
        """Test drop_empty with conditionals that return None."""
        expressions = {
            "with_value": "if($value > 10, $value, $[default])",
            "without_value": "if($value < 5, $value, $[default])",
            "always": "$data",
        }
        context = {"value": 15, "data": "present"}
        config = DRLConfig(drop_empty=True)

        result = interpret_dict(expressions, context, config)

        # First returns 15, second returns None, third returns "present"
        assert result == {
            "with_value": 15,
            "always": "present",
        }
        assert "without_value" not in result

    def test_drop_empty_preserves_empty_nested_dict(self):
        """Test that empty nested dicts are kept (not None)."""
        expressions = {
            "empty_nested": {},
            "none_value": "$[missing]",
            "real_value": "$value",
        }
        context = {"value": "test"}
        config = DRLConfig(drop_empty=True)

        result = interpret_dict(expressions, context, config)

        assert result == {
            "empty_nested": {},  # Empty dict is kept (not None)
            "real_value": "test",
        }
        assert "none_value" not in result

    def test_drop_empty_with_function_returning_none(self):
        """Test drop_empty with custom function that returns None."""

        def return_none():
            return None

        expressions = {
            "none_func": "return_none()",
            "present": "$value",
        }
        context = {"value": "hello"}
        config = DRLConfig(
            drop_empty=True, custom_functions={"return_none": return_none}
        )

        result = interpret_dict(expressions, context, config)

        assert result == {
            "present": "hello",
        }
        assert "none_func" not in result
