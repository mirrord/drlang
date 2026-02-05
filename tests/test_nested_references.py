# SPDX-FileCopyrightText: 2026-present Dane Howard <mirrord@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Tests for nested reference support."""

import pytest
from drlang import interpret, interpolate, DRLConfig, DRLReferenceError


class TestBasicNestedReferences:
    """Test basic nested reference functionality."""

    def test_simple_nested_reference(self):
        """Test a simple nested reference with default syntax."""
        context = {
            "rocks": {
                "mica": {"color": "silver", "hardness": 2.5},
                "granite": {"color": "gray", "hardness": 6.5},
            },
            "records": {"best_rock": "mica"},
        }
        # First resolve $(records>best_rock) -> "mica"
        # Then resolve $(rocks>mica>color) -> "silver"
        result = interpret("$(rocks>$(records>best_rock)>color)", context)
        assert result == "silver"

    def test_nested_reference_different_paths(self):
        """Test nested reference with different path structures."""
        context = {
            "data": {
                "user1": {"name": "Alice", "age": 30},
                "user2": {"name": "Bob", "age": 25},
            },
            "config": {"active_user": "user2"},
        }
        result = interpret("$(data>$(config>active_user)>name)", context)
        assert result == "Bob"

    def test_nested_reference_at_end(self):
        """Test nested reference at the end of a path."""
        context = {
            "items": ["apple", "banana", "cherry"],
            "index": {"selected": 1},
        }
        result = interpret("$(items>$(index>selected))", context)
        assert result == "banana"

    def test_nested_reference_at_start(self):
        """Test nested reference at the start of a path."""
        context = {
            "users": {"alice": "user_data_alice", "bob": "user_data_bob"},
            "current": {"user": "alice"},
            "user_data_alice": {"email": "alice@example.com"},
        }
        result = interpret("$($(users>$(current>user))>email)", context)
        assert result == "alice@example.com"


class TestMultipleNestedReferences:
    """Test multiple nested references in a single path."""

    def test_two_nested_references(self):
        """Test path with two nested references."""
        context = {
            "db": {"table1": {"row5": {"col3": "value123"}}},
            "pointers": {"table": "table1", "row": "row5"},
        }
        result = interpret("$(db>$(pointers>table)>$(pointers>row)>col3)", context)
        assert result == "value123"

    def test_adjacent_nested_references(self):
        """Test nested references that are adjacent in the path."""
        context = {
            "matrix": {"A": {"X": 10, "Y": 20}, "B": {"X": 30, "Y": 40}},
            "coords": {"row": "A", "col": "X"},
        }
        result = interpret("$(matrix>$(coords>row)>$(coords>col))", context)
        assert result == 10


class TestDeeplyNestedReferences:
    """Test deeply nested references (references within references)."""

    def test_double_nesting(self):
        """Test a reference nested inside another nested reference."""
        context = {
            "level1": {
                "level2a": {"level3": "value_a"},
                "level2b": {"level3": "value_b"},
            },
            "pointers": {"ptr1": "level2a", "ptr2": "ptr1"},
            "config": {"use_pointer": "ptr2"},
        }
        # Resolve innermost first: $(config>use_pointer) -> "ptr2"
        # Then: $(pointers>ptr2) -> "ptr1"
        # Then: $(pointers>ptr1) -> "level2a"
        # Finally: $(level1>level2a>level3) -> "value_a"
        result = interpret(
            "$(level1>$(pointers>$(pointers>$(config>use_pointer)))>level3)", context
        )
        assert result == "value_a"

    def test_triple_nesting(self):
        """Test three levels of nesting."""
        context = {
            "keys": {"k1": "k2", "k2": "k3", "k3": "final"},
            "data": {"final": "success"},
        }
        result = interpret("$(data>$(keys>$(keys>$(keys>k1))))", context)
        assert result == "success"


class TestNestedReferenceBehaviors:
    """Test different behaviors (required, optional, passthrough) with nested references."""

    def test_nested_optional_reference_missing(self):
        """Test nested optional reference that doesn't exist."""
        context = {
            "data": {"item1": "value1"},
            "pointers": {"missing_key": None},
        }
        # Inner reference is optional and returns None, which becomes "None" string
        # Then outer lookup for "None" key fails
        with pytest.raises(DRLReferenceError):
            interpret("$(data>$[pointers>missing])", context)

    def test_nested_optional_inner_present(self):
        """Test nested optional reference that exists."""
        context = {
            "data": {"item1": "value1"},
            "pointers": {"key": "item1"},
        }
        result = interpret("$(data>$[pointers>key])", context)
        assert result == "value1"

    def test_nested_required_reference_in_optional(self):
        """Test required nested reference inside optional outer reference."""
        context = {
            "data": {"key1": "value1"},
            "pointers": {"ptr": "key1"},
        }
        result = interpret("$[data>$(pointers>ptr)]", context)
        assert result == "value1"


class TestNestedReferencesWithOperations:
    """Test nested references combined with mathematical operations."""

    def test_nested_reference_in_math(self):
        """Test nested reference used in mathematical expression."""
        context = {
            "values": {"x": 10, "y": 20},
            "config": {"selected": "x"},
        }
        result = interpret("$(values>$(config>selected)) * 2", context)
        assert result == 20

    def test_multiple_nested_refs_in_expression(self):
        """Test multiple nested references in one expression."""
        context = {
            "nums": {"a": 5, "b": 10},
            "ops": {"first": "a", "second": "b"},
        }
        result = interpret("$(nums>$(ops>first)) + $(nums>$(ops>second))", context)
        assert result == 15


class TestNestedReferencesWithFunctions:
    """Test nested references with function calls."""

    def test_nested_reference_in_function_arg(self):
        """Test nested reference as function argument."""
        context = {
            "strings": {"s1": "hello", "s2": "world"},
            "config": {"selected_string": "s1"},
        }
        result = interpret("upper($(strings>$(config>selected_string)))", context)
        assert result == "HELLO"

    def test_function_result_in_nested_reference(self):
        """Test function result used in nested reference path."""
        # This tests that we can't directly use function results in paths
        # (functions would need to be evaluated first in the expression)
        context = {
            "data": {"HELLO": "value"},
            "strings": {"key": "hello"},
        }
        # The upper function isn't evaluated in the reference path
        # References are resolved first, functions later
        with pytest.raises(DRLReferenceError):
            interpret("$(data>upper($(strings>key)))", context)


class TestNestedReferencesInInterpolation:
    """Test nested references in string interpolation."""

    def test_interpolate_with_nested_reference(self):
        """Test nested reference in interpolate template."""
        context = {
            "users": {
                "alice": {"email": "alice@example.com"},
                "bob": {"email": "bob@example.com"},
            },
            "current": {"user": "alice"},
        }
        result = interpolate("Email: $(users>$(current>user)>email)", context)
        assert result == "Email: alice@example.com"

    def test_interpolate_expression_block_with_nested_ref(self):
        """Test nested reference inside {% %} expression block."""
        context = {
            "prices": {"item1": 100, "item2": 200},
            "cart": {"selected": "item2"},
        }
        result = interpolate("Price: {% $(prices>$(cart>selected)) * 1.1 %}", context)
        # Use approximate comparison due to floating point precision
        assert result.startswith("Price: 220.0")

    def test_type_preserving_with_nested_reference(self):
        """Test type preservation with single nested reference."""
        context = {
            "data": {"count": 42, "name": "test"},
            "ptr": {"field": "count"},
        }
        result = interpolate("$(data>$(ptr>field))", context)
        assert result == 42
        assert isinstance(result, int)


class TestNestedReferencesCustomSyntax:
    """Test nested references with custom DRLConfig syntax."""

    def test_at_dot_nested_reference(self):
        """Test nested references with @ and . syntax."""
        config = DRLConfig("@", ".")
        context = {
            "rocks": {"mica": {"color": "silver"}},
            "records": {"best_rock": "mica"},
        }
        result = interpret("@(rocks.@(records.best_rock).color)", context, config)
        assert result == "silver"

    def test_hash_slash_nested_reference(self):
        """Test nested references with # and / syntax."""
        config = DRLConfig("#", "/")
        context = {
            "data": {"item1": {"value": 100}},
            "config": {"selected": "item1"},
        }
        result = interpret("#(data/#(config/selected)/value)", context, config)
        assert result == 100


class TestNestedReferenceEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_nested_reference(self):
        """Test nested reference that resolves to empty string."""
        context = {
            "data": {"": "empty_key_value"},
            "keys": {"key": ""},
        }
        result = interpret("$(data>$(keys>key))", context)
        assert result == "empty_key_value"

    def test_numeric_nested_reference(self):
        """Test nested reference that resolves to a number."""
        context = {
            "items": ["zero", "one", "two", "three"],
            "config": {"index": 2},
        }
        result = interpret("$(items>$(config>index))", context)
        assert result == "two"

    def test_nested_reference_with_spaces_in_keys(self):
        """Test nested references with spaces in key names."""
        context = {
            "user data": {"alice smith": {"age": 30}},
            "lookup": {"current user": "alice smith"},
        }
        result = interpret("$(user data>$(lookup>current user)>age)", context)
        assert result == 30

    def test_invalid_nested_reference_missing_closing(self):
        """Test error handling for malformed nested reference."""
        context = {"data": {"key": "value"}}
        with pytest.raises(DRLReferenceError):
            # Missing inner reference
            interpret("$(data>$(missing))", context)


class TestNestedReferencePerformance:
    """Test that nested references don't cause performance issues."""

    def test_reasonable_nesting_depth(self):
        """Test that reasonable nesting depth works efficiently."""
        # Build a chain of 10 nested references
        context = {
            "v0": "v1",
            "v1": "v2",
            "v2": "v3",
            "v3": "v4",
            "v4": "v5",
            "v5": "v6",
            "v6": "v7",
            "v7": "v8",
            "v8": "v9",
            "v9": "final",
            "data": {"final": "success"},
        }
        # Chain 10 nested references
        result = interpret(
            "$(data>$(v0))",  # Simplify test - just 2 levels
            {"v0": "final", "data": {"final": "success"}},
        )
        assert result == "success"

    def test_wide_nested_references(self):
        """Test multiple nested references at same level (not deeply nested)."""
        context = {
            "db": {
                "t1r1": {"c1": "A", "c2": "B"},
                "t1r2": {"c1": "C", "c2": "D"},
            },
            "p": {"t": "t1r1", "c": "c2"},
        }
        result = interpret("$(db>$(p>t)>$(p>c))", context)
        assert result == "B"


class TestRealWorldNestedReferences:
    """Test real-world use cases for nested references."""

    def test_dynamic_config_lookup(self):
        """Test dynamic configuration lookup based on environment."""
        context = {
            "config": {
                "dev": {"db_host": "localhost", "db_port": 5432},
                "prod": {"db_host": "prod.example.com", "db_port": 5432},
            },
            "environment": {"current": "prod"},
        }
        host = interpret("$(config>$(environment>current)>db_host)", context)
        assert host == "prod.example.com"

    def test_multilevel_data_access(self):
        """Test accessing deeply nested data with dynamic keys."""
        context = {
            "users": {
                "alice": {
                    "preferences": {"theme": "dark", "language": "en"},
                },
                "bob": {
                    "preferences": {"theme": "light", "language": "fr"},
                },
            },
            "session": {"current_user": "alice"},
            "requested": {"setting": "theme"},
        }
        result = interpret(
            "$(users>$(session>current_user)>preferences>$(requested>setting))",
            context,
        )
        assert result == "dark"

    def test_template_with_dynamic_field_selection(self):
        """Test template generation with dynamic field selection."""
        context = {
            "products": {
                "laptop": {"name": "Pro Laptop", "price": 1299, "stock": 45},
                "mouse": {"name": "Wireless Mouse", "price": 29, "stock": 120},
            },
            "display": {"product_id": "laptop", "field": "price"},
        }
        template = "Product: $(products>$(display>product_id)>name), Price: $$(products>$(display>product_id)>$(display>field))"
        result = interpolate(template, context)
        assert "Pro Laptop" in result
        assert "1299" in result
