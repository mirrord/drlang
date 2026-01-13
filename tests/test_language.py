# SPDX-FileCopyrightText: 2026-present Dane Howard <mirrord@gmail.com>
#
# SPDX-License-Identifier: MIT
import pytest
from drlang.language import (
    tokenize,
    resolve_reference,
    parse_line,
    interpret,
    Token,
)
from drlang import DRLReferenceError, DRLTypeError, DRLNameError


class TestTokenize:
    """Test the tokenizer."""

    def test_tokenize_simple_reference(self):
        tokens = tokenize("$root>timestamp")
        assert len(tokens) == 1
        assert tokens[0].type == "REFERENCE"
        assert tokens[0].value == "root>timestamp"

    def test_tokenize_reference_with_spaces(self):
        tokens = tokenize("$houses>Maryland City>occupants")
        assert len(tokens) == 1
        assert tokens[0].type == "REFERENCE"
        assert tokens[0].value == "houses>Maryland City>occupants"

    def test_tokenize_function_call(self):
        tokens = tokenize("print($root>timestamp)")
        assert len(tokens) == 4
        assert tokens[0].type == "FUNCTION"
        assert tokens[0].value == "print"
        assert tokens[1].type == "LPAREN"
        assert tokens[2].type == "REFERENCE"
        assert tokens[2].value == "root>timestamp"
        assert tokens[3].type == "RPAREN"

    def test_tokenize_function_with_string_arg(self):
        tokens = tokenize("split($data>names, ',')")
        assert tokens[0].type == "FUNCTION"
        assert tokens[0].value == "split"
        assert tokens[2].type == "REFERENCE"
        assert tokens[2].value == "data>names"
        assert tokens[3].type == "COMMA"
        assert tokens[4].type == "STRING"
        assert tokens[4].value == ","

    def test_tokenize_string_literals(self):
        tokens = tokenize("'single' \"double\"")
        assert len(tokens) == 2
        assert tokens[0].type == "STRING"
        assert tokens[0].value == "single"
        assert tokens[1].type == "STRING"
        assert tokens[1].value == "double"

    def test_tokenize_empty_string(self):
        tokens = tokenize("")
        assert len(tokens) == 0


class TestResolveReference:
    """Test reference resolution."""

    def test_resolve_simple_key(self):
        context = {"timestamp": 1234}
        result = resolve_reference("timestamp", context)
        assert result == 1234

    def test_resolve_nested_keys(self):
        context = {"root": {"timestamp": 1234}}
        result = resolve_reference("root>timestamp", context)
        assert result == 1234

    def test_resolve_deeply_nested(self):
        context = {"a": {"b": {"c": {"d": "value"}}}}
        result = resolve_reference("a>b>c>d", context)
        assert result == "value"

    def test_resolve_key_with_spaces(self):
        context = {"houses": {"Maryland City": {"occupants": "John,Jane"}}}
        result = resolve_reference("houses>Maryland City>occupants", context)
        assert result == "John,Jane"

    def test_resolve_missing_key(self):
        context = {"root": {}}
        with pytest.raises(DRLReferenceError):
            resolve_reference("root>missing", context)

    def test_resolve_non_dict_value(self):
        context = {"root": "not a dict"}
        with pytest.raises(DRLTypeError):
            resolve_reference("root>timestamp", context)


class TestParseLine:
    """Test expression parsing."""

    def test_parse_simple_reference(self):
        result = parse_line("$root>timestamp")
        assert isinstance(result, Token)
        assert result.type == "REFERENCE"

    def test_parse_function_no_args(self):
        result = parse_line("test()")
        assert isinstance(result, list)
        assert result[0] == "test"
        assert len(result) == 1

    def test_parse_function_one_arg(self):
        result = parse_line("print($root>timestamp)")
        assert isinstance(result, list)
        assert result[0] == "print"
        assert len(result) == 2
        assert isinstance(result[1], Token)
        assert result[1].type == "REFERENCE"

    def test_parse_function_multiple_args(self):
        result = parse_line("split($data>names, ',')")
        assert isinstance(result, list)
        assert result[0] == "split"
        assert len(result) == 3
        assert result[1].type == "REFERENCE"
        assert result[2].type == "STRING"

    def test_parse_empty_expression(self):
        result = parse_line("")
        assert result is None


class TestInterpret:
    """Test the main interpret function."""

    def test_interpret_simple_reference(self):
        context = {"root": {"timestamp": 1234}}
        result = interpret("$root>timestamp", context)
        assert result == 1234

    def test_interpret_nested_reference(self):
        context = {"a": {"b": {"c": "value"}}}
        result = interpret("$a>b>c", context)
        assert result == "value"

    def test_interpret_split_function(self):
        context = {"data": {"names": "alice,bob,charlie"}}
        result = interpret("split($data>names, ',')", context)
        assert result == ["alice", "bob", "charlie"]

    def test_interpret_split_with_spaces(self):
        context = {"data": {"items": "apple, banana, cherry"}}
        result = interpret("split($data>items, ', ')", context)
        assert result == ["apple", "banana", "cherry"]

    def test_interpret_key_with_spaces(self):
        context = {"houses": {"Maryland City": {"occupants": "John,Jane,Jack"}}}
        result = interpret("split($houses>Maryland City>occupants, ',')", context)
        assert result == ["John", "Jane", "Jack"]

    def test_interpret_print_function(self, capsys):
        context = {"root": {"timestamp": 1234}}
        result = interpret("print($root>timestamp)", context)
        captured = capsys.readouterr()
        assert "1234" in captured.out
        assert result is None  # print returns None

    def test_interpret_missing_function(self):
        context = {"data": "value"}
        with pytest.raises(DRLNameError, match="Function 'nonexistent' not found"):
            interpret("nonexistent(data)", context)

    def test_interpret_missing_reference(self):
        context = {"root": {}}
        with pytest.raises(DRLReferenceError):
            interpret("$(root>missing)", context)

    def test_interpret_complex_nested_data(self):
        context = {
            "config": {
                "servers": {"production": {"host": "prod.example.com", "port": "8080"}}
            }
        }
        result = interpret("$config>servers>production>host", context)
        assert result == "prod.example.com"

    def test_interpret_multiple_levels(self):
        context = {"level1": {"level2": {"level3": {"level4": {"level5": "deep"}}}}}
        result = interpret("$level1>level2>level3>level4>level5", context)
        assert result == "deep"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_context(self):
        with pytest.raises(DRLReferenceError):
            interpret("$(key)", {})

    def test_whitespace_handling(self):
        context = {"key": "value"}
        result = interpret("  $key  ", context)
        assert result == "value"

    def test_special_characters_in_string(self):
        context = {"data": {"text": "hello,world"}}
        result = interpret("split($data>text, ',')", context)
        assert result == ["hello", "world"]

    def test_numeric_values(self):
        context = {"numbers": {"count": 42}}
        result = interpret("$numbers>count", context)
        assert result == 42

    def test_list_values(self):
        context = {"items": {"list": [1, 2, 3]}}
        result = interpret("$items>list", context)
        assert result == [1, 2, 3]

    def test_boolean_values(self):
        context = {"flags": {"enabled": True}}
        result = interpret("$flags>enabled", context)
        assert result is True

    def test_none_value(self):
        context = {"data": {"value": None}}
        result = interpret("$data>value", context)
        assert result is None


class TestRealWorldScenarios:
    """Test real-world usage scenarios from README."""

    def test_readme_example_1(self, capsys):
        """Test first README example: print($root>timestamp)"""
        source_data = {"root": {"timestamp": "2026-01-12T10:30:00Z"}}
        config_item = "print($root>timestamp)"
        interpret(config_item, source_data)

        captured = capsys.readouterr()
        assert "2026-01-12T10:30:00Z" in captured.out

    def test_readme_example_2(self):
        """Test second README example: split with Maryland City"""
        source_data = {"houses": {"Maryland City": {"occupants": "Alice,Bob,Charlie"}}}
        config_item = "split($houses>Maryland City>occupants, ',')"
        people = interpret(config_item, source_data)

        assert people == ["Alice", "Bob", "Charlie"]

    def test_json_like_structure(self):
        """Test with JSON-like nested structures."""
        source_data = {
            "users": {
                "admin": {
                    "name": "Administrator",
                    "email": "admin@example.com",
                    "roles": "superuser,moderator,user",
                }
            }
        }

        result = interpret("split($users>admin>roles, ',')", source_data)
        assert result == ["superuser", "moderator", "user"]
