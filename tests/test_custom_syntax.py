"""Tests for custom syntax configuration with DRLConfig."""

import pytest
from drl import interpret, DRLConfig


class TestCustomReferenceIndicators:
    """Test different reference indicator symbols."""

    def test_default_dollar_sign(self):
        """Test default $ reference indicator."""
        result = interpret("$value", {"value": 42})
        assert result == 42

    def test_at_symbol(self):
        """Test @ as reference indicator."""
        config = DRLConfig("@", ">")
        result = interpret("@value", {"value": 42}, config)
        assert result == 42

    def test_hash_symbol(self):
        """Test # as reference indicator."""
        config = DRLConfig("#", ">")
        result = interpret("#value", {"value": 42}, config)
        assert result == 42

    def test_ampersand_symbol(self):
        """Test & as reference indicator."""
        config = DRLConfig("&", ">")
        result = interpret("&value", {"value": 42}, config)
        assert result == 42

    def test_invalid_reference_indicator(self):
        """Test that invalid reference indicators are rejected."""
        with pytest.raises(ValueError, match="conflicts with reserved syntax"):
            DRLConfig("(", ">")  # Parentheses not allowed


class TestCustomKeyDelimiters:
    """Test different key delimiter symbols."""

    def test_default_greater_than(self):
        """Test default > key delimiter."""
        result = interpret("$a>b>c", {"a": {"b": {"c": 99}}})
        assert result == 99

    def test_dot_delimiter(self):
        """Test . as key delimiter."""
        config = DRLConfig("$", ".")
        result = interpret("$a.b.c", {"a": {"b": {"c": 99}}}, config)
        assert result == 99

    def test_slash_delimiter(self):
        """Test / as key delimiter."""
        config = DRLConfig("$", "/")
        result = interpret("$a/b/c", {"a": {"b": {"c": 99}}}, config)
        assert result == 99

    def test_double_colon_delimiter(self):
        """Test :: as key delimiter."""
        config = DRLConfig("$", "::")
        result = interpret("$a::b::c", {"a": {"b": {"c": 99}}}, config)
        assert result == 99

    def test_pipe_delimiter(self):
        """Test | as key delimiter."""
        config = DRLConfig("$", "|")
        result = interpret("$a|b|c", {"a": {"b": {"c": 99}}}, config)
        assert result == 99


class TestCombinedCustomSyntax:
    """Test combinations of custom reference indicators and key delimiters."""

    def test_at_dot_combination(self):
        """Test @var.key syntax (JavaScript-like)."""
        config = DRLConfig("@", ".")
        data = {"user": {"name": "Alice", "age": 30}}
        assert interpret("@user.name", data, config) == "Alice"
        assert interpret("@user.age", data, config) == 30

    def test_hash_slash_combination(self):
        """Test #var/key syntax (path-like)."""
        config = DRLConfig("#", "/")
        data = {"root": {"path": {"to": {"value": "found"}}}}
        result = interpret("#root/path/to/value", data, config)
        assert result == "found"

    def test_ampersand_doublecolon_combination(self):
        """Test &var::key syntax (C++-like)."""
        config = DRLConfig("&", "::")
        data = {"namespace": {"class": {"method": "result"}}}
        result = interpret("&namespace::class::method", data, config)
        assert result == "result"


class TestKeysWithSpaces:
    """Test that keys with spaces work with custom syntax."""

    def test_spaces_with_default_syntax(self):
        """Test spaces in keys with default $ and >."""
        data = {"user info": {"full name": "John Doe"}}
        result = interpret("$user info>full name", data)
        assert result == "John Doe"

    def test_spaces_with_dot_delimiter(self):
        """Test spaces in keys with . delimiter."""
        config = DRLConfig("@", ".")
        data = {"user info": {"full name": "Jane Smith"}}
        result = interpret("@user info.full name", data, config)
        assert result == "Jane Smith"

    def test_spaces_with_slash_delimiter(self):
        """Test spaces in keys with / delimiter."""
        config = DRLConfig("#", "/")
        data = {"my data": {"some key": 123}}
        result = interpret("#my data/some key", data, config)
        assert result == 123


class TestCustomSyntaxWithOperators:
    """Test custom syntax with mathematical operators."""

    def test_addition_with_at_dot(self):
        """Test addition with @. syntax."""
        config = DRLConfig("@", ".")
        result = interpret("@x + @y", {"x": 10, "y": 5}, config)
        assert result == 15

    def test_multiplication_with_hash_slash(self):
        """Test multiplication with #/ syntax."""
        config = DRLConfig("#", "/")
        data = {"a": {"b": {"c": 7}}}
        result = interpret("#a/b/c * 2", data, config)
        assert result == 14

    def test_complex_expression_with_custom_syntax(self):
        """Test complex expression with custom syntax."""
        config = DRLConfig("@", ".")
        data = {"price": 100, "tax": 0.1, "discount": 10}
        result = interpret("(@price * (1 + @tax)) - @discount", data, config)
        assert result == pytest.approx(100.0)  # Use approx for floating point

    def test_operator_precedence_with_custom_syntax(self):
        """Test operator precedence is maintained with custom syntax."""
        config = DRLConfig("&", "::")
        data = {"a": 2, "b": 3, "c": 4}
        result = interpret("&a + &b * &c", data, config)
        assert result == 14  # 2 + (3 * 4) = 14


class TestCustomSyntaxWithFunctions:
    """Test custom syntax with function calls."""

    def test_split_with_at_dot(self):
        """Test split function with @. syntax."""
        config = DRLConfig("@", ".")
        data = {"data": {"names": "alice,bob,charlie"}}
        result = interpret('split(@data.names, ",")', data, config)
        assert result == ["alice", "bob", "charlie"]

    def test_max_with_hash_slash(self):
        """Test max function with #/ syntax."""
        config = DRLConfig("#", "/")
        data = {"values": {"x": 15, "y": 20}}
        result = interpret("max(#values/x, #values/y)", data, config)
        assert result == 20

    def test_upper_with_ampersand_colon(self):
        """Test upper function with &:: syntax."""
        config = DRLConfig("&", "::")
        data = {"text": {"message": "hello world"}}
        result = interpret("upper(&text::message)", data, config)
        assert result == "HELLO WORLD"

    def test_nested_functions_with_custom_syntax(self):
        """Test nested functions with custom syntax."""
        config = DRLConfig("@", ".")
        data = {"nums": "10,20,30"}
        result = interpret('max(split(@nums, ","))', data, config)
        assert result == "30"  # String comparison


class TestCustomSyntaxEdgeCases:
    """Test edge cases with custom syntax."""

    def test_single_level_reference(self):
        """Test single-level reference with custom syntax."""
        config = DRLConfig("@", ".")
        result = interpret("@value", {"value": "test"}, config)
        assert result == "test"

    def test_deeply_nested_reference(self):
        """Test deeply nested reference."""
        config = DRLConfig("#", "/")
        data = {"a": {"b": {"c": {"d": {"e": {"f": "deep"}}}}}}
        result = interpret("#a/b/c/d/e/f", data, config)
        assert result == "deep"

    def test_numeric_values(self):
        """Test numeric values with custom syntax."""
        config = DRLConfig("@", ".")
        data = {"int": 42, "float": 3.14, "negative": -10}
        assert interpret("@int", data, config) == 42
        assert interpret("@float", data, config) == 3.14
        assert interpret("@negative", data, config) == -10

    def test_parentheses_with_custom_syntax(self):
        """Test parentheses grouping with custom syntax."""
        config = DRLConfig("@", ".")
        data = {"a": 5, "b": 3}
        result = interpret("(@a + @b) * 2", data, config)
        assert result == 16

    def test_power_operator_with_custom_syntax(self):
        """Test power operator with custom syntax."""
        config = DRLConfig("#", "/")
        data = {"base": 2, "exp": 3}
        result = interpret("#base ^ #exp", data, config)
        assert result == 8


class TestMultipleConfigsInSameSession:
    """Test using multiple configs in the same session."""

    def test_switching_between_configs(self):
        """Test that different configs can be used independently."""
        data1 = {"value": 10}
        data2 = {"value": 20}

        config1 = DRLConfig("@", ".")
        config2 = DRLConfig("#", "/")

        result1 = interpret("@value", data1, config1)
        result2 = interpret("#value", data2, config2)

        assert result1 == 10
        assert result2 == 20

    def test_default_and_custom_configs(self):
        """Test that default and custom configs work together."""
        data = {"x": 100}

        # Default config
        result_default = interpret("$x", data)
        assert result_default == 100

        # Custom config
        config = DRLConfig("@", ".")
        result_custom = interpret("@x", data, config)
        assert result_custom == 100
