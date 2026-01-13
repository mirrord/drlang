"""Demonstration of reference behaviors: () required, [] optional, {} literal."""

from drlang import interpret, DRLReferenceError

print("=" * 70)
print("DRLang Reference Behavior Demo")
print("=" * 70)

# Example data
data = {
    "user": {"name": "Alice", "email": "alice@example.com"},
    "settings": {"theme": "dark", "notifications": True},
}

# ============================================================================
# OPTIONAL REFERENCES $[ref]
# ============================================================================
print("\n1. Optional References $[ref] - Returns None when missing:")
print("-" * 70)

# Access existing value
result = interpret("$[user>name]", data)
print(f"$[user>name] = {result}")  # "Alice"

# Access missing value - returns None instead of error
result = interpret("$[user>age]", data)
print(f"$[user>age] = {result}")  # None

# Safe navigation - returns None if any part of path is missing
result = interpret("$[user>profile>bio]", data)
print(f"$[user>profile>bio] = {result}")  # None

# ============================================================================
# REQUIRED REFERENCES $(ref)
# ============================================================================
print("\n2. Required References $(ref) - Raises error when missing:")
print("-" * 70)

# Access existing value
result = interpret("$(user>name)", data)
print(f"$(user>name) = {result}")  # "Alice"

# Try to access missing value - raises error
try:
    result = interpret("$(user>age)", data)
    print(f"$(user>age) = {result}")
except DRLReferenceError as e:
    print(f"$(user>age) → Error: {str(e).split(chr(10))[0]}")

# ============================================================================
# LITERAL FALLBACK ${ref}
# ============================================================================
print("\n3. Literal Fallback ${ref} - Returns original string when missing:")
print("-" * 70)

# Access existing value
result = interpret("${user>name}", data)
print(f"${{user>name}} = {result}")  # "Alice"

# Access missing value - returns the original reference string
result = interpret("${user>age}", data)
print(f"${{user>age}} = {result}")  # "$user>age"

# Useful for template strings where you want to preserve placeholders
result = interpret('"${user>name} is ${user>age} years old"', data)
print(f"Template result: {result}")  # "Alice is $user>age years old"

# ============================================================================
# PRACTICAL USE CASES
# ============================================================================
print("\n4. Practical Use Cases:")
print("-" * 70)

# Use Case 1: Provide default values with optional references
print("\n▸ Use Case 1: Default Values")
expr = "if($[user>age], $[user>age], 18)"
result = interpret(expr, data)
print(f"  Age with default: {result}")  # 18 (default because age is missing)

# Use Case 2: Safe navigation pattern
print("\n▸ Use Case 2: Safe Navigation")
expr = 'if($[settings>advanced>cache], "enabled", "disabled")'
result = interpret(expr, data)
print(f"  Cache setting: {result}")  # "disabled" (safe - doesn't error)

# Use Case 3: Required fields validation
print("\n▸ Use Case 3: Required Fields")
try:
    # Ensure critical field exists
    result = interpret("$(settings>database_url)", data)
except DRLReferenceError:
    print("  ✗ Critical field 'database_url' is missing (as expected)")

# Use Case 4: Mixed optional and required
print("\n▸ Use Case 4: Mixed References")
# Use optional to check, required to access
expr = 'if($[user>verified], ($user>email), "unverified")'
result = interpret(expr, data)
print(f"  Email check: {result}")  # "unverified" (verified field is missing)

# Add verified field
data["user"]["verified"] = True
result = interpret(expr, data)
print(f"  After adding verified: {result}")  # "alice@example.com"

# Use Case 5: Template strings with literal fallback
print("\n▸ Use Case 5: Template Strings")
template = '"Hello ${user>name}, your balance is ${account>balance}"'
result = interpret(template, data)
print(f"  Template: {result}")  # Preserves missing placeholders

# ============================================================================
# CONFIGURATION WITH OPTIONAL REFERENCES
# ============================================================================
print("\n5. Configuration Management Pattern:")
print("-" * 70)

config_data = {
    "app": {"name": "MyApp", "version": "1.0.0"},
    "server": {"host": "localhost", "port": 8080},
}

# Build connection string with defaults
# Required: name, host, port (use () for validation)
# Optional: ssl, timeout (use [] for safe access with defaults)
expr = "$(app>name)"
app_name = interpret(expr.strip(), config_data)
print(f"  App name (required): {app_name}")

# Port with default
expr = "if($[server>port], $[server>port], 80)"
port = interpret(expr, config_data)
print(f"  Port (with default): {port}")

# SSL with default
expr = 'if($[server>ssl], "https", "http")'
protocol = interpret(expr, config_data)
print(f"  Protocol (with default): {protocol}")

# Timeout with default
expr = "if($[server>timeout], $[server>timeout], 30)"
timeout = interpret(expr, config_data)
print(f"  Timeout (with default): {timeout}")

# ============================================================================
# MIGRATION GUIDE
# ============================================================================
print("\n6. Reference Syntax Summary:")
print("-" * 70)
print("  • $[ref]  - Optional: Returns None if missing (safe navigation)")
print("  • $(ref)  - Required: Raises error if missing (validation)")
print("  • ${ref}  - Literal: Returns '$ref' string if missing (templates)")
print("  • $ref    - Bare: Depends on implementation (check docs)")

print("\n  Use Cases:")
print("    $[ref]  → Safe defaults: if($[age], $[age], 18)")
print("    $(ref)  → Validation: $(api_key) ensures it exists")
print("    ${ref}  → Templates: 'Hello ${name}' preserves placeholders")

print("\n" + "=" * 70)
print("Demo complete!")
print("=" * 70)
