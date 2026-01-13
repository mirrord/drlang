"""
Demo script showcasing DRL's customizable syntax feature.

This example shows how you can use different symbols for reference indicators
and key delimiters to match your preferred coding style.
"""

from drlang import interpret, DRLConfig

# Sample data structure
user_data = {
    "user": {"name": "Alice", "age": 30, "email": "alice@example.com"},
    "settings": {"theme": "dark", "notifications": True},
    "stats": {"posts": 42, "followers": 150},
}

print("=" * 60)
print("DRLang Custom Syntax Demo")
print("=" * 60)

# Default syntax: $ and >
print("\n1. Default Syntax ($ and >)")
print("-" * 40)
print("Expression: $user>name")
print(f"Result: {interpret('$user>name', user_data)}")
print("\nExpression: $stats>posts * 2")
print(f"Result: {interpret('$stats>posts * 2', user_data)}")

# JavaScript-style: @ and .
print("\n2. JavaScript-style Syntax (@ and .)")
print("-" * 40)
config_js = DRLConfig("@", ".")
print("Expression: @user.email")
print(f"Result: {interpret('@user.email', user_data, config_js)}")
print("\nExpression: upper(@settings.theme)")
print(f"Result: {interpret('upper(@settings.theme)', user_data, config_js)}")

# Path-style: # and /
print("\n3. Path-style Syntax (# and /)")
print("-" * 40)
config_path = DRLConfig("#", "/")
print("Expression: #user/name")
print(f"Result: {interpret('#user/name', user_data, config_path)}")
print("\nExpression: #stats/followers + #stats/posts")
print(f"Result: {interpret('#stats/followers + #stats/posts', user_data, config_path)}")

# C++-style: & and ::
print("\n4. C++-style Syntax (& and ::)")
print("-" * 40)
config_cpp = DRLConfig("&", "::")
print("Expression: &user::age")
print(f"Result: {interpret('&user::age', user_data, config_cpp)}")
print("\nExpression: (&user::age * 12) / 365")
print(
    f"Result: {interpret('(&user::age * 12) / 365', user_data, config_cpp):.2f} (age in months per day)"
)

# Complex example with nested data
print("\n5. Complex Example with Calculations")
print("-" * 40)
data = {"product": {"price": 100, "discount": 15, "tax_rate": 0.08}}
config = DRLConfig("@", ".")
expression = "(@product.price - @product.discount) * (1 + @product.tax_rate)"
print("Data: Product price=$100, discount=$15, tax=8%")
print(f"Expression: {expression}")
result = interpret(expression, data, config)
print(f"Final price: ${result:.2f}")

# Example with keys containing spaces
print("\n6. Keys with Spaces")
print("-" * 40)
space_data = {"user info": {"full name": "Bob Smith", "home address": "123 Main St"}}
config = DRLConfig("@", ".")
print("Expression: @user info.full name")
print(f"Result: {interpret('@user info.full name', space_data, config)}")

# Function combinations
print("\n7. Functions with Custom Syntax")
print("-" * 40)
tags_data = {"tags": "python,programming,drl,syntax"}
config = DRLConfig("#", "/")
expression = 'len(split(#tags, ","))'
print(f"Expression: {expression}")
result = interpret(expression, tags_data, config)
print(f"Result: {result} tags")

print("\n" + "=" * 60)
print("Demo complete! Try your own custom syntax combinations.")
print("=" * 60)
