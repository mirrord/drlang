#!/usr/bin/env python3
"""
Demo: Nested Reference Support in DRLang

This example demonstrates how to use nested references where
inner references are resolved first and their values used in
the outer reference path.
"""

from drlang import interpret, interpolate, DRLConfig

print("=" * 70)
print("DRLang Nested Reference Demo")
print("=" * 70)

# Example 1: Basic Nested Reference
print("\n1. Basic Nested Reference")
print("-" * 70)

context1 = {
    "rocks": {
        "mica": {"color": "silver", "hardness": 2.5},
        "granite": {"color": "gray", "hardness": 6.5},
        "quartz": {"color": "clear", "hardness": 7.0},
    },
    "records": {"best_rock": "mica"},
}

expression = "$(rocks>$(records>best_rock)>color)"
print(f"Context: {context1}")
print(f"Expression: {expression}")
print(f"Resolution:")
print(f"  1. $(records>best_rock) → 'mica'")
print(f"  2. $(rocks>mica>color) → 'silver'")
result = interpret(expression, context1)
print(f"Result: {result}")

# Example 2: Dynamic User Data Access
print("\n2. Dynamic User Data Access")
print("-" * 70)

context2 = {
    "users": {
        "alice": {"name": "Alice Smith", "email": "alice@example.com", "role": "admin"},
        "bob": {"name": "Bob Jones", "email": "bob@example.com", "role": "user"},
    },
    "session": {"current_user": "alice"},
}

expression = "$(users>$(session>current_user)>email)"
print(f"Current User: {context2['session']['current_user']}")
print(f"Expression: {expression}")
result = interpret(expression, context2)
print(f"Email: {result}")

# Example 3: Multiple Nested References
print("\n3. Multiple Nested References in One Path")
print("-" * 70)

context3 = {
    "database": {
        "users_table": {
            "row_5": {"name": "John", "age": 30},
            "row_10": {"name": "Jane", "age": 25},
        }
    },
    "pointers": {"table_name": "users_table", "row_id": "row_10"},
}

expression = "$(database>$(pointers>table_name)>$(pointers>row_id)>name)"
print(f"Expression: {expression}")
print(f"Resolution:")
print(f"  1. $(pointers>table_name) → 'users_table'")
print(f"  2. $(pointers>row_id) → 'row_10'")
print(f"  3. $(database>users_table>row_10>name) → 'Jane'")
result = interpret(expression, context3)
print(f"Result: {result}")

# Example 4: Deeply Nested References
print("\n4. Deeply Nested References (Nested within Nested)")
print("-" * 70)

context4 = {
    "data": {
        "item1": {"value": "found it!"},
        "item2": {"value": "something else"},
    },
    "keys": {"k1": "k2", "k2": "k3", "k3": "item1"},
}

expression = "$(data>$(keys>$(keys>$(keys>k1)))>value)"
print(f"Expression: {expression}")
print(f"Resolution:")
print(f"  1. $(keys>k1) → 'k2'")
print(f"  2. $(keys>k2) → 'k3'")
print(f"  3. $(keys>k3) → 'item1'")
print(f"  4. $(data>item1>value) → 'found it!'")
result = interpret(expression, context4)
print(f"Result: {result}")

# Example 5: Nested References in String Interpolation
print("\n5. Nested References in String Interpolation")
print("-" * 70)

context5 = {
    "products": {
        "laptop": {"name": "Pro Laptop", "price": 1299, "stock": 45},
        "mouse": {"name": "Wireless Mouse", "price": 29, "stock": 120},
    },
    "cart": {"selected_item": "laptop"},
}

template = "Product: $(products>$(cart>selected_item)>name), Price: $$(products>$(cart>selected_item)>price)"
print(f"Template: {template}")
result = interpolate(template, context5)
print(f"Result: {result}")

# Example 6: Nested References with Mathematical Operations
print("\n6. Nested References with Mathematical Operations")
print("-" * 70)

context6 = {
    "prices": {"item1": 100, "item2": 200, "item3": 300},
    "config": {"selected": "item2", "tax_rate": 0.1},
}

expression = "$(prices>$(config>selected)) * (1 + $config>tax_rate)"
print(f"Expression: {expression}")
result = interpret(expression, context6)
print(f"Result: ${result:.2f}")

# Example 7: Real-World Example - Environment-Based Configuration
print("\n7. Real-World: Environment-Based Configuration")
print("-" * 70)

context7 = {
    "config": {
        "dev": {
            "db_host": "localhost",
            "db_port": 5432,
            "api_url": "http://localhost:3000",
        },
        "prod": {
            "db_host": "prod.example.com",
            "db_port": 5432,
            "api_url": "https://api.example.com",
        },
    },
    "environment": {"current": "prod"},
}

print(f"Current Environment: {context7['environment']['current']}")
db_host = interpret("$(config>$(environment>current)>db_host)", context7)
api_url = interpret("$(config>$(environment>current)>api_url)", context7)
print(f"Database Host: {db_host}")
print(f"API URL: {api_url}")

# Example 8: Using Custom Syntax
print("\n8. Nested References with Custom Syntax (@.)")
print("-" * 70)

config = DRLConfig("@", ".")
context8 = {
    "themes": {
        "dark": {"primary": "#000", "secondary": "#333"},
        "light": {"primary": "#fff", "secondary": "#ccc"},
    },
    "settings": {"theme": "dark"},
}

expression = "@(themes.@(settings.theme).primary)"
print(f"Custom Syntax: @. (JavaScript-like)")
print(f"Expression: {expression}")
result = interpret(expression, context8, config)
print(f"Primary Color: {result}")

# Example 9: Optional Nested References
print("\n9. Optional Nested References")
print("-" * 70)

context9 = {
    "users": {"alice": {"email": "alice@example.com"}},
    "session": {"user_id": "bob"},  # bob doesn't exist
}

# Using optional reference $[...] to avoid errors
template = "User Email: $[users>$(session>user_id)>email]"
print(f"Template: {template}")
result = interpolate(template, context9)
print(f"Result: {result}")
print("(Empty result because 'bob' user doesn't exist, but no error thrown)")

print("\n" + "=" * 70)
print("Demo Complete!")
print("=" * 70)
