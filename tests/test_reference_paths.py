# SPDX-FileCopyrightText: 2026-present Dane Howard <mirrord@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for special characters in reference paths including spaces and parentheses."""

from drlang import interpret, interpolate, DRLConfig
from drlang.language import tokenize, resolve_reference


class TestSpacesInReferencePaths:
    """Test keys with spaces in reference paths."""

    def test_single_key_with_space(self):
        """Test a single key containing spaces."""
        context = {"first name": "Alice"}
        assert interpret("$first name", context) == "Alice"

    def test_nested_keys_with_spaces(self):
        """Test nested keys where multiple levels contain spaces."""
        context = {"user profile": {"home address": {"zip code": "12345"}}}
        assert interpret("$user profile>home address>zip code", context) == "12345"

    def test_spaces_at_key_boundaries(self):
        """Test that leading/trailing spaces in reference path parts are trimmed."""
        context = {"user": {"name": "Bob"}}
        # The key delimiter separates parts, and each part is trimmed
        # So "user > name" becomes ["user", "name"] after split and trim
        assert interpret("$user>name", context) == "Bob"
        # Test with bracketed syntax where internal spaces are allowed
        assert interpret("$( user > name )", context) == "Bob"

    def test_multiple_spaces_in_key(self):
        """Test keys with multiple consecutive spaces."""
        context = {"New   York   City": {"population": 8_000_000}}
        assert interpret("$New   York   City>population", context) == 8_000_000

    def test_space_in_key_with_function(self):
        """Test key with space used inside a function call."""
        context = {"tag list": "python,javascript,rust"}
        result = interpret("split($tag list, ',')", context)
        assert result == ["python", "javascript", "rust"]

    def test_space_in_key_with_operators(self):
        """Test key with space used with operators."""
        context = {"item count": 10, "unit price": 5}
        assert interpret("$item count * $unit price", context) == 50

    def test_space_in_interpolate(self):
        """Test key with space in interpolate function using bracketed syntax.

        Note: Bare references in interpolate stop at spaces for readability.
        Use bracketed syntax $(key with spaces) for keys containing spaces.
        """
        context = {"user name": "Charlie"}
        assert interpolate("Hello $(user name)!", context) == "Hello Charlie!"

    def test_space_in_interpolate_nested(self):
        """Test nested keys with spaces in interpolate using bracketed syntax."""
        context = {"user info": {"display name": "Diana"}}
        assert (
            interpolate("Welcome $(user info>display name)!", context)
            == "Welcome Diana!"
        )


class TestParenthesesInReferencePaths:
    """Test keys with parentheses in reference paths.

    Since parentheses are stop characters in bare references, bracketed syntax
    must be used: $(key(with)parens) or $[key(with)parens] or ${key(with)parens}
    """

    def test_parens_in_key_required_syntax(self):
        """Test key with parentheses using required $(ref) syntax."""
        context = {"func(x)": "result"}
        assert interpret("$(func(x))", context) == "result"

    def test_parens_in_key_optional_syntax(self):
        """Test key with parentheses using optional $[ref] syntax."""
        context = {"getValue()": 42}
        assert interpret("$[getValue()]", context) == 42

    def test_parens_in_key_passthrough_syntax(self):
        """Test key with parentheses using passthrough ${ref} syntax."""
        context = {"call()": "executed"}
        assert interpret("${call()}", context) == "executed"

    def test_parens_in_nested_key(self):
        """Test nested keys with parentheses."""
        context = {"methods": {"getData()": {"return": "value"}}}
        assert interpret("$(methods>getData()>return)", context) == "value"

    def test_parens_missing_key_optional(self):
        """Test optional reference with parens returns None when missing."""
        context = {"other": "value"}
        assert interpret("$[missing()]", context) is None

    def test_parens_missing_key_passthrough(self):
        """Test passthrough reference with parens returns original string."""
        context = {"other": "value"}
        assert interpret("${missing()}", context) == "$missing()"

    def test_parens_in_key_with_function(self):
        """Test key with parentheses used as function argument."""
        context = {"items(all)": "a,b,c"}
        result = interpret("split($(items(all)), ',')", context)
        assert result == ["a", "b", "c"]

    def test_parens_in_interpolate_required(self):
        """Test key with parentheses in interpolate using required syntax."""
        context = {"getName()": "Echo"}
        assert interpolate("Hello $(getName())!", context) == "Hello Echo!"

    def test_parens_in_interpolate_optional(self):
        """Test key with parentheses in interpolate using optional syntax."""
        context = {"getTitle()": "Dr."}
        assert interpolate("$[getTitle()] Smith", context) == "Dr. Smith"

    def test_parens_in_interpolate_passthrough(self):
        """Test passthrough with parens preserves original in interpolate."""
        context = {}
        result = interpolate("Call ${method()} for help", context)
        assert result == "Call ${method()} for help"

    def test_balanced_parens_in_key(self):
        """Test keys with balanced nested parentheses."""
        context = {"func(a(b))": "nested"}
        assert interpret("$(func(a(b)))", context) == "nested"

    def test_parens_with_spaces_in_key(self):
        """Test keys with both parentheses and spaces."""
        context = {"get value (default)": 100}
        assert interpret("$(get value (default))", context) == 100


class TestMixedSpecialCharactersInPaths:
    """Test combinations of special characters in reference paths."""

    def test_spaces_and_parens_combined(self):
        """Test key with both spaces and parentheses."""
        context = {"user data (primary)": {"full name (legal)": "John Doe"}}
        result = interpret("$(user data (primary)>full name (legal))", context)
        assert result == "John Doe"

    def test_special_chars_with_custom_syntax(self):
        """Test special characters with custom @ and . syntax."""
        config = DRLConfig("@", ".")
        context = {"my data": {"get value": "found"}}
        assert interpret("@my data.get value", context, config) == "found"

    def test_parens_with_custom_syntax(self):
        """Test parentheses with custom syntax."""
        config = DRLConfig("@", ".")
        context = {"method()": "result"}
        assert interpret("@(method())", context, config) == "result"

    def test_complex_key_structure(self):
        """Test complex nested structure with various special characters."""
        context = {
            "API Response": {"getData()": {"user info": {"full name": "Alice Smith"}}}
        }
        result = interpret("$(API Response>getData()>user info>full name)", context)
        assert result == "Alice Smith"


class TestInterpolateWithSpecialPaths:
    """Test interpolate function with special characters in paths."""

    def test_interpolate_mixed_references(self):
        """Test interpolate with multiple references containing special chars.

        Note: Keys with spaces need bracketed syntax in interpolate.
        """
        context = {"user name": "Bob", "getValue()": 42}
        template = "User: $(user name), Value: $(getValue())"
        result = interpolate(template, context)
        assert result == "User: Bob, Value: 42"

    def test_interpolate_expression_block_with_special_keys(self):
        """Test expression blocks with special character keys."""
        context = {"item count": 5, "unit price": 10}
        template = "Total: {% $item count * $unit price %}"
        result = interpolate(template, context)
        assert result == "Total: 50"

    def test_interpolate_parens_in_expression_block(self):
        """Test expression block with parenthesized key reference."""
        context = {"getMultiplier()": 3, "value": 10}
        template = "Result: {% $(getMultiplier()) * $value %}"
        result = interpolate(template, context)
        assert result == "Result: 30"


class TestTokenizerWithSpecialPaths:
    """Test tokenizer handling of special characters in reference paths."""

    def test_tokenize_space_in_reference(self):
        """Test tokenizer correctly captures spaces in references."""
        tokens = tokenize("$user name")
        assert len(tokens) == 1
        assert tokens[0].type == "REFERENCE"
        assert tokens[0].value == "user name"

    def test_tokenize_bracketed_parens(self):
        """Test tokenizer captures parentheses in bracketed references."""
        tokens = tokenize("$(method())")
        assert len(tokens) == 1
        assert tokens[0].type == "REFERENCE"
        assert tokens[0].value == "method()"
        assert tokens[0].behavior == "required"

    def test_tokenize_optional_with_parens(self):
        """Test tokenizer with optional reference containing parens."""
        tokens = tokenize("$[getValue()]")
        assert len(tokens) == 1
        assert tokens[0].type == "REFERENCE"
        assert tokens[0].value == "getValue()"
        assert tokens[0].behavior == "optional"


class TestResolveReferenceWithSpecialPaths:
    """Test resolve_reference function with special characters."""

    def test_resolve_space_in_key(self):
        """Test resolving a key with spaces."""
        context = {"my key": "my value"}
        result = resolve_reference("my key", context)
        assert result == "my value"

    def test_resolve_nested_space_keys(self):
        """Test resolving nested keys with spaces."""
        context = {"level one": {"level two": "deep value"}}
        result = resolve_reference("level one>level two", context)
        assert result == "deep value"

    def test_resolve_parens_in_key(self):
        """Test resolving a key containing parentheses."""
        context = {"func()": "called"}
        result = resolve_reference("func()", context)
        assert result == "called"

    def test_resolve_complex_key(self):
        """Test resolving complex keys with multiple special chars."""
        context = {"get data (v2)": {"response body": "success"}}
        result = resolve_reference("get data (v2)>response body", context)
        assert result == "success"
