"""Tests for custom user-provided functions in DRL."""

import pytest
from drlang import interpret, DRLConfig, register_function


class TestCustomFunctions:
    """Test custom function registration and usage."""

    def test_custom_function_in_config(self):
        """Test registering a custom function via config."""

        # Define a custom function
        def double(x):
            return x * 2

        # Create config with custom function
        config = DRLConfig(custom_functions={"double": double})

        # Use the custom function
        result = interpret("double(5)", {}, config)
        assert result == 10

    def test_multiple_custom_functions(self):
        """Test registering multiple custom functions."""

        def triple(x):
            return x * 3

        def greet(name):
            return f"Hello, {name}!"

        config = DRLConfig(custom_functions={"triple": triple, "greet": greet})

        assert interpret("triple(4)", {}, config) == 12
        assert interpret('greet("World")', {}, config) == "Hello, World!"

    def test_register_function_helper(self):
        """Test the register_function helper."""
        config = DRLConfig()

        # Register a function using the helper
        def square(x):
            return x * x

        register_function("square", square, config)

        result = interpret("square(7)", {}, config)
        assert result == 49

    def test_custom_function_with_references(self):
        """Test custom functions with data references."""

        def add_tax(price, rate):
            return price * (1 + rate)

        config = DRLConfig(custom_functions={"add_tax": add_tax})
        data = {"price": 100, "tax_rate": 0.1}

        result = interpret("add_tax($price, $tax_rate)", data, config)
        assert result == pytest.approx(110)

    def test_custom_function_with_multiple_args(self):
        """Test custom function with multiple arguments."""

        def calculate_total(price, quantity, discount):
            return price * quantity * (1 - discount)

        config = DRLConfig(custom_functions={"calculate_total": calculate_total})

        result = interpret("calculate_total(100, 5, 0.2)", {}, config)
        assert result == 400

    def test_custom_function_overrides_builtin(self):
        """Test that custom functions take precedence over built-ins."""

        # Override the 'max' function
        def custom_max(*args):
            return min(args)  # Intentionally return min instead

        config = DRLConfig(custom_functions={"max": custom_max})

        # With custom function, 'max' should return the minimum
        result = interpret("max(1, 5, 3)", {}, config)
        assert result == 1

        # Without config, should use built-in max
        result = interpret("max(1, 5, 3)", {})
        assert result == 5

    def test_custom_function_with_type_conversion(self):
        """Test custom function with type hints."""

        def concat_numbers(a: int, b: int) -> str:
            return str(a) + str(b)

        config = DRLConfig(custom_functions={"concat_numbers": concat_numbers})

        result = interpret("concat_numbers(12, 34)", {}, config)
        assert result == "1234"

    def test_custom_function_in_expressions(self):
        """Test custom functions in complex expressions."""

        def discount(price, percent):
            return price * (1 - percent / 100)

        config = DRLConfig(custom_functions={"discount": discount})

        # Use custom function in arithmetic expression
        result = interpret("discount(100, 20) + 10", {}, config)
        assert result == 90

    def test_nested_custom_functions(self):
        """Test nesting custom functions."""

        def double(x):
            return x * 2

        def add_ten(x):
            return x + 10

        config = DRLConfig(custom_functions={"double": double, "add_ten": add_ten})

        result = interpret("double(add_ten(5))", {}, config)
        assert result == 30  # (5 + 10) * 2

    def test_custom_function_with_if(self):
        """Test custom functions with if() function."""

        def is_adult(age):
            return age >= 18

        config = DRLConfig(custom_functions={"is_adult": is_adult})

        result = interpret('if(is_adult(25), "adult", "minor")', {}, config)
        assert result == "adult"

        result = interpret('if(is_adult(15), "adult", "minor")', {}, config)
        assert result == "minor"

    def test_custom_function_returns_dict(self):
        """Test custom function that returns a dict."""

        def make_person(name, age):
            return {"name": name, "age": age}

        config = DRLConfig(custom_functions={"make_person": make_person})

        result = interpret('make_person("Alice", 30)', {}, config)
        assert result == {"name": "Alice", "age": 30}

    def test_custom_function_with_variadic_args(self):
        """Test custom function with variable number of arguments."""

        def sum_all(*args):
            return sum(args)

        config = DRLConfig(custom_functions={"sum_all": sum_all})

        result = interpret("sum_all(1, 2, 3, 4, 5)", {}, config)
        assert result == 15

    def test_lambda_as_custom_function(self):
        """Test using lambda functions as custom functions."""
        config = DRLConfig(
            custom_functions={
                "cube": lambda x: x**3,
                "is_even": lambda n: n % 2 == 0,
            }
        )

        assert interpret("cube(3)", {}, config) == 27
        assert interpret("is_even(4)", {}, config) is True
        assert interpret("is_even(5)", {}, config) is False

    def test_custom_function_with_default_args(self):
        """Test custom function with default arguments."""

        def multiply(a, b=10):
            return a * b

        config = DRLConfig(custom_functions={"multiply": multiply})

        # With both args
        assert interpret("multiply(5, 3)", {}, config) == 15

        # With default arg (note: DRL doesn't support default args syntax,
        # but the function itself has defaults)
        assert interpret("multiply(5)", {}, config) == 50

    def test_custom_syntax_with_custom_functions(self):
        """Test custom functions work with custom syntax."""

        def double(x):
            return x * 2

        config = DRLConfig(
            ref_indicator="@",
            key_delimiter=".",
            custom_functions={"double": double},
        )

        data = {"value": 15}
        result = interpret("double(@value)", data, config)
        assert result == 30

    def test_error_on_undefined_function(self):
        """Test that calling an undefined function raises an error."""
        with pytest.raises(NameError, match="Function 'undefined' not found"):
            interpret("undefined(5)", {})

    def test_register_globally(self):
        """Test registering a function globally."""

        def quadruple(x):
            return x * 4

        # Register globally (no config)
        register_function("quadruple", quadruple)

        # Should be available without config
        result = interpret("quadruple(5)", {})
        assert result == 20

        # Clean up the global registry
        from drlang.functions import FUNCTIONS

        if "quadruple" in FUNCTIONS:
            del FUNCTIONS["quadruple"]


class TestRealWorldCustomFunctions:
    """Test real-world use cases for custom functions."""

    def test_data_validation(self):
        """Test custom validation functions."""

        def validate_email(email):
            return "@" in email and "." in email

        def validate_age(age):
            return 0 < age < 120

        config = DRLConfig(
            custom_functions={
                "validate_email": validate_email,
                "validate_age": validate_age,
            }
        )

        data = {"email": "user@example.com", "age": 25}

        result = interpret(
            'if(validate_email($email) and validate_age($age), "valid", "invalid")',
            data,
            config,
        )
        assert result == "valid"

    def test_business_logic(self):
        """Test custom business logic functions."""

        def calculate_discount(price, customer_type):
            discounts = {"premium": 0.2, "regular": 0.1, "new": 0.05}
            return price * (1 - discounts.get(customer_type, 0))

        config = DRLConfig(custom_functions={"calculate_discount": calculate_discount})

        data = {"price": 100, "customer": "premium"}
        result = interpret("calculate_discount($price, $customer)", data, config)
        assert result == 80

    def test_data_transformation(self):
        """Test custom data transformation functions."""

        def format_phone(number):
            # Simple formatter: (123) 456-7890
            digits = "".join(filter(str.isdigit, str(number)))
            if len(digits) == 10:
                return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            return number

        config = DRLConfig(custom_functions={"format_phone": format_phone})

        result = interpret('format_phone("1234567890")', {}, config)
        assert result == "(123) 456-7890"

    def test_complex_calculation(self):
        """Test complex calculation with multiple custom functions."""

        def calculate_bmi(weight, height):
            return weight / (height * height)

        def bmi_category(bmi):
            if bmi < 18.5:
                return "Underweight"
            elif bmi < 25:
                return "Normal"
            elif bmi < 30:
                return "Overweight"
            else:
                return "Obese"

        config = DRLConfig(
            custom_functions={
                "calculate_bmi": calculate_bmi,
                "bmi_category": bmi_category,
            }
        )

        data = {"weight": 70, "height": 1.75}  # kg, meters

        # Calculate BMI and get category
        bmi_expr = "calculate_bmi($weight, $height)"
        bmi = interpret(bmi_expr, data, config)
        assert 22.0 < bmi < 23.0

        category_expr = f"bmi_category({bmi})"
        category = interpret(category_expr, data, config)
        assert category == "Normal"
