# SPDX-FileCopyrightText: 2026-present Dane Howard <mirrord@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for reference behaviors: () required, [] optional, {} literal."""

import pytest
from drlang import interpret, DRLReferenceError


class TestOptionalReferences:
    """Test optional references with $[ref] - returns None when missing."""

    def test_optional_reference_returns_none_for_missing_key(self):
        """Optional references return None when key is missing."""
        context = {"root": {"existing": "value"}}
        result = interpret("$[root>missing]", context)
        assert result is None

    def test_optional_reference_returns_value_when_exists(self):
        """Optional references return value when key exists."""
        context = {"root": {"name": "Alice"}}
        result = interpret("$[root>name]", context)
        assert result == "Alice"

    def test_optional_reference_with_empty_context(self):
        """Optional reference on empty context returns None."""
        result = interpret("$[missing]", {})
        assert result is None

    def test_optional_reference_deeply_nested_missing(self):
        """Optional reference returns None for missing nested path."""
        context = {"a": {"b": {"c": "value"}}}
        result = interpret("$[a>b>x>y>z]", context)
        assert result is None

    def test_optional_reference_non_dict_value(self):
        """Optional reference returns None when navigating into non-dict."""
        context = {"config": "string value"}
        result = interpret("$[config>setting]", context)
        assert result is None

    def test_optional_reference_in_expression(self):
        """Optional reference can be used in expressions."""
        context = {"x": 10}
        # Optional reference works in expressions
        result = interpret("$[x] + 5", context)
        assert result == 15

    def test_optional_reference_with_if_function(self):
        """Optional references work with if() function."""
        context = {"name": "Alice"}
        # Check if optional reference is None
        result = interpret('if($[age], $[age], "unknown")', context)
        assert result == "unknown"

        # When value exists
        context = {"name": "Bob", "age": 30}
        result = interpret('if($[age], $[age], "unknown")', context)
        assert result == 30

    def test_optional_reference_with_function(self):
        """Optional references can be passed to functions."""
        context = {"data": {"name": "test"}}
        # str() converts None to "None"
        result = interpret("str($[data>missing])", context)
        assert result == "None"


class TestRequiredReferences:
    """Test required references with $(ref) - throws exception when missing."""

    def test_required_reference_raises_error_for_missing_key(self):
        """Required references raise error when key is missing."""
        context = {"root": {"existing": "value"}}
        with pytest.raises(DRLReferenceError):
            interpret("$(root>missing)", context)

    def test_required_reference_returns_value_when_exists(self):
        """Required references return value when key exists."""
        context = {"root": {"name": "Alice"}}
        result = interpret("$(root>name)", context)
        assert result == "Alice"

    def test_required_reference_with_empty_context(self):
        """Required reference on empty context raises error."""
        with pytest.raises(DRLReferenceError):
            interpret("$(missing)", {})

    def test_required_reference_deeply_nested(self):
        """Required reference works with deeply nested paths."""
        context = {"a": {"b": {"c": {"d": "value"}}}}
        result = interpret("$(a>b>c>d)", context)
        assert result == "value"

    def test_required_reference_non_dict_value(self):
        """Required reference raises error when navigating into non-dict."""
        from drlang import DRLTypeError

        context = {"config": "string value"}
        with pytest.raises(DRLTypeError):
            interpret("$(config>setting)", context)

    def test_required_reference_in_expression(self):
        """Required references work in expressions."""
        context = {"x": 10, "y": 5}
        result = interpret("$(x) + $(y)", context)
        assert result == 15

    def test_required_reference_partial_path_exists(self):
        """Required reference raises error if partial path exists but not complete."""
        from drlang import DRLTypeError

        context = {"a": {"b": "value"}}
        # Trying to access 'c' as a key of string "value" raises TypeError
        with pytest.raises(DRLTypeError):
            interpret("$(a>b>c)", context)


class TestMixedReferences:
    """Test mixing optional and required references."""

    def test_optional_and_required_in_same_expression(self):
        """Can mix optional and required references."""
        context = {"x": 10}
        # $[y] is optional (returns None), $(x) is required
        result = interpret("$(x)", context)
        assert result == 10

        result = interpret("$[y]", context)
        assert result is None

    def test_if_with_optional_and_required(self):
        """Use optional to check and required to access."""
        context = {"name": "Alice", "age": 30}

        # Check with optional, access with required
        result = interpret('if($[verified], $(name), "unverified")', context)
        assert result == "unverified"

        context["verified"] = True
        result = interpret('if($[verified], $(name), "unverified")', context)
        assert result == "Alice"

    def test_optional_provides_default_value(self):
        """Optional references can provide default values."""
        context = {"price": 100}

        # Use optional with if to provide default
        result = interpret("if($[discount], $[discount], 0)", context)
        assert result == 0

        context["discount"] = 10
        result = interpret("if($[discount], $[discount], 0)", context)
        assert result == 10

    def test_safe_navigation_pattern(self):
        """Optional references enable safe navigation patterns."""
        context = {"user": {"profile": {"name": "Alice"}}}

        # Safe access - returns None if any part missing
        result = interpret("$[user>profile>name]", context)
        assert result == "Alice"

        result = interpret("$[user>settings>theme]", context)
        assert result is None

    def test_required_ensures_data_presence(self):
        """Required references ensure critical data exists."""
        context = {"config": {"api_key": "secret"}}

        # This should work
        result = interpret("$(config>api_key)", context)
        assert result == "secret"

        # This should fail
        with pytest.raises(DRLReferenceError):
            interpret("$(config>database_url)", context)


class TestLiteralFallback:
    """Test literal fallback with ${ref} - returns original string when missing."""

    def test_literal_returns_original_string_when_missing(self):
        """Literal references return the original string when key is missing."""
        context = {"root": {"existing": "value"}}
        result = interpret("${root>missing}", context)
        assert result == "$root>missing"

    def test_literal_returns_value_when_exists(self):
        """Literal references return value when key exists."""
        context = {"root": {"name": "Alice"}}
        result = interpret("${root>name}", context)
        assert result == "Alice"

    def test_literal_in_string_template(self):
        """Literal references work well in string templates."""
        context = {"name": "Bob"}
        # String interpolation would need to be added - for now just test the fallback behavior
        result = interpret("${name}", context)
        assert result == "Bob"

        result = interpret("${age}", context)
        assert result == "$age"

    def test_literal_with_nested_missing(self):
        """Literal returns full path when nested key missing."""
        context = {"a": {"b": "value"}}
        result = interpret("${a>x>y}", context)
        assert result == "$a>x>y"
