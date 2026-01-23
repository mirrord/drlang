# SPDX-FileCopyrightText: 2026-present Dane Howard <mirrord@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for string interpolation with the interpolate and interpolate_dict functions."""

import pytest
from drlang import (
    interpolate,
    interpolate_dict,
    DRLConfig,
    DRLSyntaxError,
    DRLReferenceError,
)


class TestLiteralStrings:
    """Test that strings without special markers are treated as literals."""

    def test_plain_string(self):
        """Plain strings are returned unchanged."""
        result = interpolate("Hello, world!", {})
        assert result == "Hello, world!"

    def test_string_with_special_chars(self):
        """Strings with special characters (but not markers) are literals."""
        result = interpolate("Price: 100% off! 2+2=4", {})
        assert result == "Price: 100% off! 2+2=4"

    def test_empty_string(self):
        """Empty string returns empty string."""
        result = interpolate("", {})
        assert result == ""

    def test_whitespace_only(self):
        """Whitespace-only string is preserved."""
        result = interpolate("   \t\n  ", {})
        assert result == "   \t\n  "

    def test_curly_braces_without_percent(self):
        """Curly braces without % are treated as literals."""
        result = interpolate("{not an expression}", {})
        assert result == "{not an expression}"


class TestExpressionBlocks:
    """Test {% expression %} blocks."""

    def test_simple_expression(self):
        """Simple expression block is evaluated."""
        result = interpolate("Sum is {% 2 + 3 %}", {})
        assert result == "Sum is 5"

    def test_expression_with_reference(self):
        """Expression block can contain references."""
        result = interpolate("Result: {% $value * 2 %}", {"value": 10})
        assert result == "Result: 20"

    def test_expression_with_function(self):
        """Expression block can contain function calls."""
        result = interpolate("Upper: {% upper('hello') %}", {})
        assert result == "Upper: HELLO"

    def test_multiple_expression_blocks(self):
        """Multiple expression blocks in one string."""
        result = interpolate("{% 1 + 1 %} and {% 2 + 2 %}", {})
        assert result == "2 and 4"

    def test_expression_block_with_whitespace(self):
        """Whitespace inside expression blocks is handled."""
        result = interpolate("{%   5 + 5   %}", {})
        assert result == "10"

    def test_complex_expression(self):
        """Complex expression with operators and precedence."""
        result = interpolate("{% (2 + 3) * 4 %}", {})
        assert result == "20"

    def test_expression_returns_none(self):
        """Expression returning None becomes empty string."""
        result = interpolate("Value: {% $[missing] %}", {"other": 1})
        assert result == "Value: "


class TestReferenceInterpolation:
    """Test $reference interpolation."""

    def test_simple_reference(self):
        """Simple reference is resolved."""
        result = interpolate("Hello, $name!", {"name": "Alice"})
        assert result == "Hello, Alice!"

    def test_nested_reference(self):
        """Nested reference with key delimiter."""
        result = interpolate(
            "Path: $data>nested>value", {"data": {"nested": {"value": "found"}}}
        )
        assert result == "Path: found"

    def test_reference_at_start(self):
        """Reference at the start of string."""
        result = interpolate("$greeting world", {"greeting": "Hello"})
        assert result == "Hello world"

    def test_reference_at_end(self):
        """Reference at the end of string."""
        result = interpolate("Say $word", {"word": "goodbye"})
        assert result == "Say goodbye"

    def test_multiple_references(self):
        """Multiple references in one string."""
        result = interpolate("$first and $second", {"first": "one", "second": "two"})
        assert result == "one and two"

    def test_reference_with_brackets_required(self):
        """Required reference with () brackets."""
        result = interpolate("Value: $(value)", {"value": 42})
        assert result == "Value: 42"

    def test_reference_with_brackets_optional(self):
        """Optional reference with [] brackets returns empty for missing."""
        result = interpolate("Value: $[missing]!", {"other": 1})
        assert result == "Value: !"

    def test_reference_with_brackets_passthrough(self):
        """Passthrough reference with {} brackets returns original for missing."""
        result = interpolate("Value: ${missing}!", {"other": 1})
        assert result == "Value: ${missing}!"


class TestMixedInterpolation:
    """Test mixing expression blocks and references."""

    def test_reference_and_expression(self):
        """Both reference and expression in same string."""
        result = interpolate(
            "Hello $name, you have {% $count * 2 %} items",
            {"name": "Alice", "count": 5},
        )
        assert result == "Hello Alice, you have 10 items"

    def test_alternating_literals_and_interpolation(self):
        """Alternating between literal text and interpolations."""
        result = interpolate("A=$a B={% $b + 1 %} C=$c", {"a": 1, "b": 2, "c": 3})
        assert result == "A=1 B=3 C=3"

    def test_consecutive_references(self):
        """Multiple references without space between."""
        result = interpolate("$first$second", {"first": "Hello", "second": "World"})
        assert result == "HelloWorld"

    def test_reference_inside_expression(self):
        """Reference inside expression block."""
        result = interpolate("{% upper($name) %}", {"name": "alice"})
        assert result == "ALICE"


class TestCustomSyntax:
    """Test interpolation with custom DRLConfig."""

    def test_custom_ref_indicator(self):
        """Custom reference indicator works."""
        config = DRLConfig("@", ">")
        result = interpolate("Hello @name!", {"name": "Bob"}, config)
        assert result == "Hello Bob!"

    def test_custom_key_delimiter(self):
        """Custom key delimiter works."""
        config = DRLConfig("$", ".")
        result = interpolate(
            "Value: $data.nested.value", {"data": {"nested": {"value": 99}}}, config
        )
        assert result == "Value: 99"

    def test_at_dot_syntax(self):
        """JavaScript-like @. syntax."""
        config = DRLConfig("@", ".")
        result = interpolate(
            "@user.name is @user.age years old",
            {"user": {"name": "Charlie", "age": 30}},
            config,
        )
        assert result == "Charlie is 30 years old"

    def test_expression_with_custom_syntax(self):
        """Expression blocks use custom syntax."""
        config = DRLConfig("@", ".")
        result = interpolate("Sum: {% @a + @b %}", {"a": 10, "b": 20}, config)
        assert result == "Sum: 30"


class TestErrorHandling:
    """Test error handling in interpolation."""

    def test_unterminated_expression_block(self):
        """Unterminated expression block raises error."""
        with pytest.raises(DRLSyntaxError, match="Unterminated expression block"):
            interpolate("{% 2 + 3", {})

    def test_missing_required_reference(self):
        """Missing required reference raises error."""
        with pytest.raises(DRLReferenceError):
            interpolate("$(missing)", {})

    def test_unterminated_bracket_reference(self):
        """Unterminated bracket reference raises error."""
        with pytest.raises(DRLSyntaxError, match="Unterminated reference"):
            interpolate("$(unclosed", {})

    def test_invalid_expression(self):
        """Invalid expression in block raises error."""
        with pytest.raises(Exception):  # Could be various DRL errors
            interpolate("{% unknown_func() %}", {})


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_percent_sign_alone(self):
        """Percent sign alone is literal."""
        result = interpolate("100% complete", {})
        assert result == "100% complete"

    def test_curly_brace_alone(self):
        """Curly brace alone is literal."""
        result = interpolate("{just braces}", {})
        assert result == "{just braces}"

    def test_empty_expression_block(self):
        """Empty expression block."""
        result = interpolate("{% %}", {})
        # Empty expression might return None or empty string
        assert result == "" or result == "None"

    def test_dollar_at_end(self):
        """Dollar sign at end of string (no reference path)."""
        result = interpolate("Price: 100$", {})
        # The $ without a path just becomes literal
        assert result == "Price: 100$"

    def test_numeric_result(self):
        """Numeric results are converted to string."""
        result = interpolate("Count: {% 42 %}", {})
        assert result == "Count: 42"
        assert isinstance(result, str)

    def test_boolean_result(self):
        """Boolean results are converted to string."""
        result = interpolate("Flag: {% True %}", {})
        assert result == "Flag: True"

    def test_list_result(self):
        """List results are converted to string."""
        result = interpolate("List: $items", {"items": [1, 2, 3]})
        assert result == "List: [1, 2, 3]"


class TestTypePreservation:
    """Test that interpolate preserves types for single references."""

    def test_single_ref_preserves_int(self):
        """Single reference preserves integer type."""
        result = interpolate("$value", {"value": 42})
        assert result == 42
        assert isinstance(result, int)

    def test_single_ref_preserves_float(self):
        """Single reference preserves float type."""
        result = interpolate("$value", {"value": 3.14})
        assert result == 3.14
        assert isinstance(result, float)

    def test_single_ref_preserves_bool(self):
        """Single reference preserves boolean type."""
        result = interpolate("$flag", {"flag": True})
        assert result is True
        assert isinstance(result, bool)

    def test_single_ref_preserves_list(self):
        """Single reference preserves list type."""
        result = interpolate("$items", {"items": [1, 2, 3]})
        assert result == [1, 2, 3]
        assert isinstance(result, list)

    def test_single_ref_preserves_dict(self):
        """Single reference preserves dict type."""
        result = interpolate("$data", {"data": {"key": "value"}})
        assert result == {"key": "value"}
        assert isinstance(result, dict)

    def test_single_ref_returns_empty_for_none(self):
        """Single optional reference returns empty string for None."""
        result = interpolate("$[missing]", {"other": "value"})
        assert result == ""
        assert isinstance(result, str)

    def test_bracketed_ref_preserves_type(self):
        """Bracketed single reference preserves type."""
        result = interpolate("$(value)", {"value": 42})
        assert result == 42
        assert isinstance(result, int)

    def test_nested_ref_preserves_type(self):
        """Nested single reference preserves type."""
        result = interpolate("$data>count", {"data": {"count": 100}})
        assert result == 100
        assert isinstance(result, int)

    def test_mixed_content_returns_string(self):
        """Mixed content with literal text returns string."""
        result = interpolate("Value: $value", {"value": 42})
        assert result == "Value: 42"
        assert isinstance(result, str)

    def test_multiple_refs_returns_string(self):
        """Multiple references return string."""
        result = interpolate("$a$b", {"a": 1, "b": 2})
        assert result == "12"
        assert isinstance(result, str)

    def test_expression_block_returns_string(self):
        """Expression block always returns string."""
        result = interpolate("{% 42 %}", {})
        assert result == "42"
        assert isinstance(result, str)

    def test_expression_block_with_ref_returns_string(self):
        """Expression block with reference returns string."""
        result = interpolate("{% $value %}", {"value": 42})
        assert result == "42"
        assert isinstance(result, str)


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_email_template(self):
        """Email template interpolation."""
        template = "Dear $name,\n\nYour order #$order>id totaling {% $order>total %} has shipped."
        context = {"name": "Customer", "order": {"id": "12345", "total": 99.99}}
        result = interpolate(template, context)
        assert "Dear Customer" in result
        assert "#12345" in result
        assert "99.99" in result

    def test_config_generation(self):
        """Configuration file generation."""
        template = 'host = "$server>host"\nport = {% $server>port %}'
        context = {"server": {"host": "localhost", "port": 8080}}
        result = interpolate(template, context)
        assert 'host = "localhost"' in result
        assert "port = 8080" in result

    def test_url_construction(self):
        """URL construction with interpolation."""
        template = "https://$domain/api/v{% $version %}/users/$user_id"
        context = {"domain": "example.com", "version": 2, "user_id": "abc123"}
        result = interpolate(template, context)
        assert result == "https://example.com/api/v2/users/abc123"


class TestInterpolateDictBasic:
    """Test basic interpolate_dict functionality."""

    def test_simple_dict(self):
        """Simple dictionary of templates."""
        templates = {
            "greeting": "Hello $name!",
            "farewell": "Goodbye $name!",
        }
        context = {"name": "Alice"}
        result = interpolate_dict(templates, context)
        assert result == {"greeting": "Hello Alice!", "farewell": "Goodbye Alice!"}

    def test_mixed_templates_and_expressions(self):
        """Mix of simple references and expression blocks."""
        templates = {
            "name": "$user>name",
            "doubled_age": "Age x2: {% $user>age * 2 %}",
        }
        context = {"user": {"name": "Bob", "age": 25}}
        result = interpolate_dict(templates, context)
        assert result == {"name": "Bob", "doubled_age": "Age x2: 50"}

    def test_non_string_values_pass_through(self):
        """Non-string values are passed through unchanged."""
        templates = {
            "name": "$user",
            "count": 42,
            "active": True,
            "ratio": 3.14,
        }
        context = {"user": "Alice"}
        result = interpolate_dict(templates, context)
        assert result == {
            "name": "Alice",
            "count": 42,
            "active": True,
            "ratio": 3.14,
        }

    def test_empty_dict(self):
        """Empty template dict returns empty dict."""
        result = interpolate_dict({}, {"any": "data"})
        assert result == {}


class TestInterpolateDictNested:
    """Test nested dictionary handling in interpolate_dict."""

    def test_nested_dict(self):
        """Nested dictionaries are processed recursively."""
        templates = {
            "user": {
                "name": "Name: $name",
                "contact": {
                    "email": "$email",
                    "phone": "$phone",
                },
            }
        }
        context = {"name": "Alice", "email": "alice@example.com", "phone": "555-1234"}
        result = interpolate_dict(templates, context)
        assert result == {
            "user": {
                "name": "Name: Alice",
                "contact": {
                    "email": "alice@example.com",
                    "phone": "555-1234",
                },
            }
        }

    def test_deeply_nested(self):
        """Deeply nested structures work correctly."""
        templates = {"a": {"b": {"c": {"d": "Value: $x"}}}}
        context = {"x": 42}
        result = interpolate_dict(templates, context)
        assert result == {"a": {"b": {"c": {"d": "Value: 42"}}}}


class TestInterpolateDictLists:
    """Test list handling in interpolate_dict."""

    def test_list_of_templates(self):
        """Lists of templates are processed."""
        templates = {"messages": ["Hello $name", "Welcome $name", "Bye $name"]}
        context = {"name": "Charlie"}
        result = interpolate_dict(templates, context)
        assert result == {
            "messages": ["Hello Charlie", "Welcome Charlie", "Bye Charlie"]
        }

    def test_list_with_non_strings(self):
        """Lists with non-string items pass through non-strings."""
        templates = {"items": ["$item1", 42, "$item2", True]}
        context = {"item1": "Apple", "item2": "Banana"}
        result = interpolate_dict(templates, context)
        assert result == {"items": ["Apple", 42, "Banana", True]}

    def test_empty_list(self):
        """Empty lists are preserved."""
        templates = {"items": []}
        result = interpolate_dict(templates, {})
        assert result == {"items": []}


class TestInterpolateListDicts:
    """Test list handling in interpolate_dict."""

    def test_list_of_templates(self):
        """Lists of templates are processed."""
        templates = {
            "messages": [{"Hello": "$name"}, {"Greeting": "{% $greeting %} Charles"}]
        }
        context = {"name": "Charlie", "greeting": "Heyo"}
        result = interpolate_dict(templates, context)
        assert result == {
            "messages": [{"Hello": "Charlie"}, {"Greeting": "Heyo Charles"}]
        }

    def test_list_of_list_of_templates(self):
        """Lists of templates are processed."""
        templates = {
            "messages": [
                [{"Hello": "$name"}, {"Greeting": "{% $greeting %} Charles"}],
                ["$item1", 42, "$item2", True],
            ]
        }
        context = {
            "name": "Charlie",
            "greeting": "Heyo",
            "item1": "Apple",
            "item2": "Banana",
        }
        result = interpolate_dict(templates, context)
        assert result == {
            "messages": [
                [{"Hello": "Charlie"}, {"Greeting": "Heyo Charles"}],
                ["Apple", 42, "Banana", True],
            ]
        }


class TestInterpolateDictDropEmpty:
    """Test drop_empty configuration in interpolate_dict."""

    def test_drop_empty_false_default(self):
        """By default, None values are kept."""
        templates = {
            "present": "$value",
            "missing": "$[missing]",  # Optional reference returns None
        }
        context = {"value": "exists"}
        result = interpolate_dict(templates, context)
        assert "present" in result
        assert "missing" in result
        assert result["missing"] == ""  # interpolate converts None to empty string

    def test_drop_empty_true(self):
        """With drop_empty=True, keys with None or empty string values are excluded."""
        config = DRLConfig(drop_empty=True)
        templates = {
            "present": "$value",
            "missing": "$[missing]",  # Returns "" (None->empty string), will be dropped
        }
        context = {"value": "exists"}
        result = interpolate_dict(templates, context, config)
        assert "present" in result
        assert "missing" not in result  # Empty strings are dropped with drop_empty=True

    def test_drop_empty_with_nested(self):
        """drop_empty works recursively on nested dicts."""
        config = DRLConfig(drop_empty=True)
        templates = {
            "outer": "Hello",
            "nested": {
                "inner": "$value",
            },
        }
        context = {"value": "World"}
        result = interpolate_dict(templates, context, config)
        assert result == {"outer": "Hello", "nested": {"inner": "World"}}

    def test_falsy_values_preserved(self):
        """Falsy values (0, False) are NOT dropped, but empty strings are."""
        config = DRLConfig(drop_empty=True)
        templates = {
            "zero": 0,
            "false_val": False,
            "empty_str": "",
        }
        result = interpolate_dict(templates, {}, config)
        assert result == {"zero": 0, "false_val": False}
        assert "empty_str" not in result  # Empty strings are dropped


class TestInterpolateDictCustomSyntax:
    """Test interpolate_dict with custom syntax configuration."""

    def test_at_dot_syntax(self):
        """Custom @. syntax works in interpolate_dict."""
        config = DRLConfig("@", ".")
        templates = {
            "name": "User: @user.name",
            "age": "Age: {% @user.age %}",
        }
        context = {"user": {"name": "Diana", "age": 28}}
        result = interpolate_dict(templates, context, config)
        assert result == {"name": "User: Diana", "age": "Age: 28"}

    def test_hash_slash_syntax(self):
        """Custom #/ syntax works in interpolate_dict."""
        config = DRLConfig("#", "/")
        templates = {
            "path": "#root/folder/file",
            "computed": "{% #x + #y %}",
        }
        context = {"root": {"folder": {"file": "data.txt"}}, "x": 10, "y": 20}
        result = interpolate_dict(templates, context, config)
        assert result == {"path": "data.txt", "computed": "30"}


class TestInterpolateDictRealWorld:
    """Test real-world usage scenarios for interpolate_dict."""

    def test_api_response_template(self):
        """Generate API response from templates."""
        templates = {
            "status": "success",
            "data": {
                "user_id": "$user>id",
                "display_name": "$user>name",
                "email": "$user>email",
            },
            "meta": {
                "request_id": "$request_id",
                "timestamp": "{% $timestamp %}",
            },
        }
        context = {
            "user": {"id": "123", "name": "Alice", "email": "alice@example.com"},
            "request_id": "req-456",
            "timestamp": "2026-01-14T10:30:00Z",
        }
        result = interpolate_dict(templates, context)
        assert result["status"] == "success"
        assert result["data"]["user_id"] == "123"
        assert result["data"]["display_name"] == "Alice"
        assert result["meta"]["request_id"] == "req-456"

    def test_config_file_generation(self):
        """Generate configuration file content."""
        templates = {
            "database": {
                "host": "$db>host",
                "port": "{% $db>port %}",
                "name": "$db>name",
            },
            "server": {
                "address": "$(server>host):{% $server>port %}",
                "debug": "{% $debug %}",
            },
        }
        context = {
            "db": {"host": "localhost", "port": 5432, "name": "myapp"},
            "server": {"host": "0.0.0.0", "port": 8080},
            "debug": False,
        }
        result = interpolate_dict(templates, context)
        assert result["database"]["host"] == "localhost"
        assert result["database"]["port"] == "5432"
        assert result["server"]["address"] == "0.0.0.0:8080"
        assert result["server"]["debug"] == "False"

    def test_email_templates(self):
        """Generate multiple email templates."""
        templates = {
            "welcome": {
                "subject": "Welcome $user>name!",
                "body": "Hello $user>name,\n\nWelcome to our service!",
            },
            "notification": {
                "subject": "New activity on your account",
                "body": "Hi $user>name,\n\nYou have {% $notifications %} new notifications.",
            },
        }
        context = {"user": {"name": "Bob"}, "notifications": 5}
        result = interpolate_dict(templates, context)
        assert result["welcome"]["subject"] == "Welcome Bob!"
        assert "Hello Bob" in result["welcome"]["body"]
        assert "5 new notifications" in result["notification"]["body"]
