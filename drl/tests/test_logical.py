"""Tests for logical operations and conditional expressions in DRL."""

from drl import interpret


class TestComparisonOperators:
    """Test comparison operators: ==, !=, <, >, <=, >="""

    def test_equality(self):
        """Test == operator."""
        assert interpret("5 == 5", {}) is True
        assert interpret("5 == 3", {}) is False
        assert interpret('"hello" == "hello"', {}) is True
        assert interpret('"hello" == "world"', {}) is False

    def test_inequality(self):
        """Test != operator."""
        assert interpret("5 != 3", {}) is True
        assert interpret("5 != 5", {}) is False
        assert interpret('"hello" != "world"', {}) is True
        assert interpret('"hello" != "hello"', {}) is False

    def test_less_than(self):
        """Test < operator."""
        assert interpret("3 < 5", {}) is True
        assert interpret("5 < 3", {}) is False
        assert interpret("5 < 5", {}) is False

    def test_greater_than(self):
        """Test > operator."""
        assert interpret("5 > 3", {}) is True
        assert interpret("3 > 5", {}) is False
        assert interpret("5 > 5", {}) is False

    def test_less_than_or_equal(self):
        """Test <= operator."""
        assert interpret("3 <= 5", {}) is True
        assert interpret("5 <= 5", {}) is True
        assert interpret("7 <= 5", {}) is False

    def test_greater_than_or_equal(self):
        """Test >= operator."""
        assert interpret("5 >= 3", {}) is True
        assert interpret("5 >= 5", {}) is True
        assert interpret("3 >= 5", {}) is False


class TestComparisonWithReferences:
    """Test comparison operators with variable references."""

    def test_equality_with_references(self):
        """Test == with references."""
        assert interpret("$x == 10", {"x": 10}) is True
        assert interpret("$x == 10", {"x": 5}) is False

    def test_two_references(self):
        """Test comparison between two references."""
        assert interpret("$x == $y", {"x": 10, "y": 10}) is True
        assert interpret("$x < $y", {"x": 5, "y": 10}) is True
        assert interpret("$x > $y", {"x": 15, "y": 10}) is True

    def test_nested_reference_comparison(self):
        """Test comparison with nested references."""
        data = {"user": {"age": 25, "score": 85}}
        assert interpret("$user>age >= 18", data) is True
        assert interpret("$user>score > 90", data) is False


class TestLogicalOperators:
    """Test logical operators: and, or, not"""

    def test_and_operator(self):
        """Test 'and' operator."""
        assert interpret("True and True", {}) is True
        assert interpret("True and False", {}) is False
        assert interpret("False and True", {}) is False
        assert interpret("False and False", {}) is False

    def test_or_operator(self):
        """Test 'or' operator."""
        assert interpret("True or True", {}) is True
        assert interpret("True or False", {}) is True
        assert interpret("False or True", {}) is True
        assert interpret("False or False", {}) is False

    def test_not_operator(self):
        """Test 'not' operator."""
        assert interpret("not True", {}) is False
        assert interpret("not False", {}) is True

    def test_complex_logical_expression(self):
        """Test combination of logical operators."""
        assert interpret("True and (False or True)", {}) is True
        assert interpret("(True and False) or True", {}) is True
        assert interpret("not (True and False)", {}) is True


class TestLogicalWithComparison:
    """Test logical operators combined with comparisons."""

    def test_and_with_comparisons(self):
        """Test 'and' with comparison operators."""
        assert interpret("5 > 3 and 10 < 20", {}) is True
        assert interpret("5 > 3 and 10 > 20", {}) is False

    def test_or_with_comparisons(self):
        """Test 'or' with comparison operators."""
        assert interpret("5 < 3 or 10 < 20", {}) is True
        assert interpret("5 < 3 or 10 > 20", {}) is False

    def test_not_with_comparison(self):
        """Test 'not' with comparison."""
        assert interpret("not 5 < 3", {}) is True
        assert interpret("not 5 > 3", {}) is False

    def test_complex_logical_comparison(self):
        """Test complex expressions with both logical and comparison operators."""
        result = interpret("(5 > 3 and 10 < 20) or (2 == 2 and 1 != 1)", {})
        assert result is True

        result = interpret("5 > 3 and (10 < 5 or 20 > 15)", {})
        assert result is True


class TestIfFunction:
    """Test the if() function for conditional logic."""

    def test_if_true_condition(self):
        """Test if() with true condition."""
        result = interpret('if(True, "yes", "no")', {})
        assert result == "yes"

    def test_if_false_condition(self):
        """Test if() with false condition."""
        result = interpret('if(False, "yes", "no")', {})
        assert result == "no"

    def test_if_with_comparison(self):
        """Test if() with comparison expression."""
        result = interpret('if(5 > 3, "greater", "lesser")', {})
        assert result == "greater"

        result = interpret('if(5 < 3, "greater", "lesser")', {})
        assert result == "lesser"

    def test_if_with_references(self):
        """Test if() with variable references."""
        data = {"age": 25}
        result = interpret('if($age >= 18, "adult", "minor")', data)
        assert result == "adult"

        data = {"age": 15}
        result = interpret('if($age >= 18, "adult", "minor")', data)
        assert result == "minor"

    def test_if_with_numeric_results(self):
        """Test if() returning numeric values."""
        result = interpret("if(5 > 3, 100, 200)", {})
        assert result == 100

        result = interpret("if(5 < 3, 100, 200)", {})
        assert result == 200

    def test_if_with_logical_operators(self):
        """Test if() with logical operators in condition."""
        result = interpret('if(5 > 3 and 10 < 20, "both true", "not both")', {})
        assert result == "both true"

        result = interpret('if(5 < 3 or 10 < 20, "at least one", "none")', {})
        assert result == "at least one"


class TestNestedConditions:
    """Test nested conditional expressions."""

    def test_nested_if(self):
        """Test nested if() functions."""
        expr = 'if($score >= 90, "A", if($score >= 80, "B", "C"))'

        assert interpret(expr, {"score": 95}) == "A"
        assert interpret(expr, {"score": 85}) == "B"
        assert interpret(expr, {"score": 75}) == "C"

    def test_if_with_expressions_in_branches(self):
        """Test if() with computed values in branches."""
        result = interpret("if(5 > 3, 10 * 2, 5 + 5)", {})
        assert result == 20

        result = interpret("if(5 < 3, 10 * 2, 5 + 5)", {})
        assert result == 10


class TestOperatorPrecedence:
    """Test that logical operators have correct precedence."""

    def test_comparison_before_logical(self):
        """Test that comparisons are evaluated before logical operators."""
        # 5 > 3 and 10 < 20 should be (5 > 3) and (10 < 20)
        result = interpret("5 > 3 and 10 < 20", {})
        assert result is True

    def test_not_before_and(self):
        """Test that 'not' has higher precedence than 'and'."""
        # not True and False should be (not True) and False
        result = interpret("not True and False", {})
        assert result is False

    def test_and_before_or(self):
        """Test that 'and' has higher precedence than 'or'."""
        # True or False and False should be True or (False and False)
        result = interpret("True or False and False", {})
        assert result is True

    def test_parentheses_override_precedence(self):
        """Test that parentheses can override precedence."""
        result = interpret("(True or False) and False", {})
        assert result is False


class TestRealWorldScenarios:
    """Test real-world conditional logic scenarios."""

    def test_age_verification(self):
        """Test age-based access control."""
        data = {"user": {"age": 25, "verified": True}}

        expr = 'if($user>age >= 18 and $user>verified, "granted", "denied")'
        result = interpret(expr, data)
        assert result == "granted"

        data["user"]["age"] = 15
        result = interpret(expr, data)
        assert result == "denied"

    def test_score_grading(self):
        """Test grade calculation based on score."""
        expr = """if($score >= 90, "A",
                     if($score >= 80, "B",
                        if($score >= 70, "C",
                           if($score >= 60, "D", "F"))))"""

        assert interpret(expr, {"score": 95}) == "A"
        assert interpret(expr, {"score": 85}) == "B"
        assert interpret(expr, {"score": 75}) == "C"
        assert interpret(expr, {"score": 65}) == "D"
        assert interpret(expr, {"score": 55}) == "F"

    def test_discount_calculation(self):
        """Test discount logic based on conditions."""
        data = {"price": 100, "member": True, "quantity": 5}

        # 10% discount for members or 5 or more items
        expr = "if($member or $quantity >= 5, $price * 0.9, $price)"
        result = interpret(expr, data)
        assert result == 90

        data["member"] = False
        data["quantity"] = 3
        result = interpret(expr, data)
        assert result == 100

    def test_temperature_classification(self):
        """Test temperature classification."""
        expr = """if($temp > 30, "hot",
                     if($temp > 20, "warm",
                        if($temp > 10, "cool", "cold")))"""

        assert interpret(expr, {"temp": 35}) == "hot"
        assert interpret(expr, {"temp": 25}) == "warm"
        assert interpret(expr, {"temp": 15}) == "cool"
        assert interpret(expr, {"temp": 5}) == "cold"

    def test_authentication_check(self):
        """Test user authentication logic."""
        data = {
            "user": {"username": "alice", "password": "secret123"},
            "input": {"username": "alice", "password": "secret123"},
        }

        expr = """if($user>username == $input>username and
                     $user>password == $input>password,
                     "authenticated", "failed")"""

        result = interpret(expr, data)
        assert result == "authenticated"

        data["input"]["password"] = "wrong"
        result = interpret(expr, data)
        assert result == "failed"


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_string_comparisons(self):
        """Test comparison of strings."""
        assert interpret('"apple" < "banana"', {}) is True
        assert interpret('"zebra" > "apple"', {}) is True
        assert interpret('"hello" == "hello"', {}) is True

    def test_mixed_type_comparisons(self):
        """Test comparisons with different types."""
        # String to number comparisons should work in Python
        result = interpret('"123" == "123"', {})
        assert result is True

    def test_boolean_values_with_if(self):
        """Test using boolean values directly."""
        assert interpret("if(True, 1, 0)", {}) == 1
        assert interpret("if(False, 1, 0)", {}) == 0

    def test_comparison_with_expressions(self):
        """Test comparisons with computed expressions."""
        result = interpret("(5 + 3) > (2 * 3)", {})
        assert result is True

        result = interpret("(10 - 5) == (2 + 3)", {})
        assert result is True

    def test_logical_with_functions(self):
        """Test logical operators with function results."""
        expr = 'len("hello") > 3 and len("world") > 3'
        result = interpret(expr, {})
        assert result is True

        expr = "max(5, 10, 3) > 8 and min(5, 10, 3) < 5"
        result = interpret(expr, {})
        assert result is True
