"""Demonstration of verbose error messages in DRL."""

from drlang import (
    interpret,
    DRLReferenceError,
    DRLNameError,
    DRLSyntaxError,
    DRLTypeError,
)

print("=" * 70)
print("DRLang Verbose Error Messages Demo")
print("=" * 70)

# Example 1: Missing reference key
print("\n1. Missing Reference Key:")
print("-" * 70)
try:
    data = {"user": {"name": "Alice"}}
    result = interpret("$user>age", data)
except DRLReferenceError as e:
    print(f"Error caught:\n{e}")

# Example 2: Non-dict navigation
print("\n2. Trying to Navigate into Non-Dictionary:")
print("-" * 70)
try:
    data = {"config": "simple string"}
    result = interpret("$config>setting>value", data)
except DRLTypeError as e:
    print(f"Error caught:\n{e}")

# Example 3: Undefined function
print("\n3. Undefined Function:")
print("-" * 70)
try:
    result = interpret("unknown_function(5, 10)", {})
except DRLNameError as e:
    print(f"Error caught:\n{e}")

# Example 4: Unterminated string
print("\n4. Unterminated String Literal:")
print("-" * 70)
try:
    result = interpret('split($data, "comma)', {"data": "a,b,c"})
except DRLSyntaxError as e:
    print(f"Error caught:\n{e}")

# Example 5: Invalid character
print("\n5. Invalid Character:")
print("-" * 70)
try:
    result = interpret("5 ! 3", {})
except DRLSyntaxError as e:
    print(f"Error caught:\n{e}")

# Example 6: Missing closing parenthesis
print("\n6. Missing Closing Parenthesis:")
print("-" * 70)
try:
    result = interpret("max(5, 10, 15", {})
except DRLSyntaxError as e:
    print(f"Error caught:\n{e}")

# Example 7: Complex nested error with context
print("\n7. Complex Expression with Nested Error:")
print("-" * 70)
try:
    data = {
        "products": {
            "electronics": {"laptop": {"price": 1000}},
            "books": {"python": {"price": 50}},
        }
    }
    # Try to access non-existent category
    result = interpret("$products>furniture>desk>price", data)
except DRLReferenceError as e:
    print(f"Error caught:\n{e}")

# Example 8: Division by zero
print("\n8. Division by Zero:")
print("-" * 70)
try:
    result = interpret("100 / (5 - 5)", {})
except DRLTypeError as e:
    print(f"Error caught:\n{e}")

print("\n" + "=" * 70)
print("Demo complete! All errors provide detailed context.")
print("=" * 70)
