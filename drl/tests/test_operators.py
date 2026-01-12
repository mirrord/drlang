# SPDX-FileCopyrightText: 2026-present Dane Howard <mirrord@gmail.com>
#
# SPDX-License-Identifier: MIT
from drl.language import interpret


class TestBasicArithmetic:
    """Test basic arithmetic operations."""

    def test_addition(self):
        assert interpret("2 + 3", {}) == 5
        assert interpret("10 + 5", {}) == 15

    def test_subtraction(self):
        assert interpret("10 - 3", {}) == 7
        assert interpret("5 - 8", {}) == -3

    def test_multiplication(self):
        assert interpret("3 * 4", {}) == 12
        assert interpret("7 * 6", {}) == 42

    def test_division(self):
        assert interpret("10 / 2", {}) == 5.0
        assert interpret("15 / 4", {}) == 3.75

    def test_modulo(self):
        assert interpret("10 % 3", {}) == 1
        assert interpret("17 % 5", {}) == 2

    def test_power(self):
        assert interpret("2 ^ 3", {}) == 8
        assert interpret("5 ^ 2", {}) == 25


class TestOperatorPrecedence:
    """Test operator precedence is handled correctly."""

    def test_multiplication_before_addition(self):
        assert interpret("2 + 3 * 4", {}) == 14  # Not 20

    def test_division_before_subtraction(self):
        assert interpret("10 - 6 / 2", {}) == 7.0  # Not 2

    def test_power_before_multiplication(self):
        assert interpret("2 * 3 ^ 2", {}) == 18  # Not 36

    def test_complex_precedence(self):
        assert interpret("2 + 3 * 4 - 1", {}) == 13
        assert interpret("10 / 2 + 3 * 2", {}) == 11.0


class TestParentheses:
    """Test parentheses override precedence."""

    def test_parentheses_override_precedence(self):
        assert interpret("(2 + 3) * 4", {}) == 20
        assert interpret("2 * (3 + 4)", {}) == 14

    def test_nested_parentheses(self):
        assert interpret("((2 + 3) * 4)", {}) == 20
        assert interpret("2 * (3 + (4 - 1))", {}) == 12

    def test_multiple_parentheses(self):
        assert interpret("(2 + 3) * (4 + 1)", {}) == 25


class TestFloatingPoint:
    """Test floating point operations."""

    def test_float_addition(self):
        assert interpret("3.14 + 2.86", {}) == 6.0

    def test_float_multiplication(self):
        result = interpret("3.14 * 2", {})
        assert abs(result - 6.28) < 0.001

    def test_mixed_int_float(self):
        assert interpret("10 / 4", {}) == 2.5
        assert interpret("3.5 * 2", {}) == 7.0


class TestWithReferences:
    """Test mathematical operations with data references."""

    def test_reference_addition(self):
        assert interpret("$x + 10", {"x": 5}) == 15

    def test_reference_multiplication(self):
        assert interpret("$value * 2", {"value": 7}) == 14

    def test_multiple_references(self):
        assert interpret("$x + $y", {"x": 3, "y": 7}) == 10
        assert interpret("$a * $b", {"a": 4, "b": 5}) == 20

    def test_reference_with_operators(self):
        assert interpret("$value * 2 + 10", {"value": 5}) == 20
        assert interpret("($x + $y) * 2", {"x": 3, "y": 2}) == 10

    def test_nested_reference(self):
        assert interpret("$data>value * 3", {"data": {"value": 4}}) == 12
        assert interpret("$a>b>c + 5", {"a": {"b": {"c": 10}}}) == 15


class TestWithFunctions:
    """Test mathematical operations combined with functions."""

    def test_function_result_in_math(self):
        assert interpret("max(5, 10) + 3", {}) == 13
        assert interpret("min(8, 3) * 2", {}) == 6

    def test_math_in_function_args(self):
        assert interpret("max(2 + 3, 4)", {}) == 5
        assert interpret("min(10 - 3, 8)", {}) == 7

    def test_complex_function_math(self):
        assert interpret("max(5, $x) + 10", {"x": 15}) == 25
        assert interpret("int(10.5) * 2", {}) == 20


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_negative_numbers(self):
        # Note: This might need special handling for unary minus
        # For now, testing with subtraction
        assert interpret("0 - 5", {}) == -5
        assert interpret("10 - 15", {}) == -5

    def test_zero_operations(self):
        assert interpret("0 + 5", {}) == 5
        assert interpret("5 * 0", {}) == 0
        assert interpret("0 ^ 5", {}) == 0

    def test_one_operations(self):
        assert interpret("5 * 1", {}) == 5
        assert interpret("1 ^ 100", {}) == 1

    def test_whitespace_handling(self):
        assert interpret("2+3", {}) == 5
        assert interpret("2  +  3", {}) == 5
        assert interpret("2+ 3", {}) == 5

    def test_complex_expression(self):
        result = interpret("((2 + 3) * 4 - 5) / 3", {})
        assert abs(result - 5.0) < 0.001


class TestRealWorldScenarios:
    """Test real-world calculation scenarios."""

    def test_percentage_calculation(self):
        assert interpret("$price * 0.15", {"price": 100}) == 15.0

    def test_area_calculation(self):
        assert interpret("$width * $height", {"width": 5, "height": 10}) == 50

    def test_temperature_conversion(self):
        # Celsius to Fahrenheit: (C * 9/5) + 32
        result = interpret("($celsius * 9 / 5) + 32", {"celsius": 0})
        assert result == 32.0

        result = interpret("($celsius * 9 / 5) + 32", {"celsius": 100})
        assert result == 212.0

    def test_compound_interest(self):
        # Simple calculation: principal * (1 + rate)^time
        result = interpret(
            "$principal * (1 + $rate) ^ $years",
            {"principal": 1000, "rate": 0.05, "years": 2},
        )
        assert abs(result - 1102.5) < 0.1
