"""Example demonstrating custom user-provided functions in DRL.

This example shows how users can register their own custom functions
to extend DRL's capabilities for domain-specific use cases.
"""

from drlang import interpret, DRLConfig, register_function


# Example 1: Simple custom function
def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


config = DRLConfig(custom_functions={"c_to_f": celsius_to_fahrenheit})

data = {"temperature": 25}
result = interpret("c_to_f($temperature)", data, config)
print(f"Example 1: {data['temperature']}°C = {result}°F")


# Example 2: Multiple custom functions for business logic
def calculate_discount(price, customer_tier):
    """Calculate discount based on customer tier."""
    discounts = {"bronze": 0.05, "silver": 0.10, "gold": 0.15, "platinum": 0.20}
    return price * discounts.get(customer_tier, 0)


def apply_tax(amount, tax_rate):
    """Apply tax to an amount."""
    return amount * (1 + tax_rate)


def calculate_shipping(weight, zone):
    """Calculate shipping cost based on weight and zone."""
    rates = {"local": 5, "regional": 10, "national": 15, "international": 25}
    base_rate = rates.get(zone, 10)
    return base_rate + (weight * 0.5)


# Register all business functions
config = DRLConfig(
    custom_functions={
        "discount": calculate_discount,
        "apply_tax": apply_tax,
        "shipping": calculate_shipping,
    }
)

# Calculate final order total
order_data = {
    "price": 100,
    "customer_tier": "gold",
    "tax_rate": 0.08,
    "weight": 2.5,
    "zone": "regional",
}

# Calculate subtotal with discount
expr = "discount($price, $customer_tier)"
subtotal = interpret(expr, order_data, config)
print(f"\nExample 2: Original price: ${order_data['price']}")
print(f"Discount ({order_data['customer_tier']}): ${order_data['price'] - subtotal}")
print(f"Subtotal: ${subtotal}")

# Add tax
order_data["subtotal"] = subtotal
expr = "apply_tax($subtotal, $tax_rate)"
with_tax = interpret(expr, order_data, config)
print(f"After tax: ${with_tax:.2f}")

# Add shipping
expr = "shipping($weight, $zone)"
shipping_cost = interpret(expr, order_data, config)
print(f"Shipping: ${shipping_cost}")
print(f"Total: ${with_tax + shipping_cost:.2f}")


# Example 3: Using custom functions with conditionals
def validate_age(age):
    """Check if age is valid."""
    return 0 < age < 150


def classify_age(age):
    """Classify age group."""
    if age < 13:
        return "child"
    elif age < 20:
        return "teenager"
    elif age < 65:
        return "adult"
    else:
        return "senior"


config = DRLConfig(
    custom_functions={"validate_age": validate_age, "classify_age": classify_age}
)

user_data = {"age": 28}

# Validate and classify age
expr = 'if(validate_age($age), classify_age($age), "invalid")'
result = interpret(expr, user_data, config)
print(f"\nExample 3: Age {user_data['age']} classified as: {result}")


# Example 4: Lambda functions
config = DRLConfig(
    custom_functions={
        "double": lambda x: x * 2,
        "is_even": lambda n: n % 2 == 0,
        "clamp": lambda value, min_val, max_val: max(min_val, min(value, max_val)),
    }
)

print("\nExample 4: Lambda functions")
print(f"double(7) = {interpret('double(7)', {}, config)}")
print(f"is_even(8) = {interpret('is_even(8)', {}, config)}")
print(f"clamp(150, 0, 100) = {interpret('clamp(150, 0, 100)', {}, config)}")


# Example 5: Register functions globally
def factorial(n):
    """Calculate factorial."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


# Register globally (available to all interpretations without config)
register_function("factorial", factorial)

result = interpret("factorial(5)", {})
print(f"\nExample 5: factorial(5) = {result}")


# Example 6: Combining custom and built-in functions
def word_count(text):
    """Count words in text."""
    return len(text.split())


config = DRLConfig(custom_functions={"word_count": word_count})

data = {"message": "Hello world from DRL"}

# Use custom function with built-in if()
expr = 'if(word_count($message) > 3, "long message", "short message")'
result = interpret(expr, data, config)
print(f"\nExample 6: '{data['message']}' is a {result}")

print("\n✓ All custom function examples completed successfully!")
