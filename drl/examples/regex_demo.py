"""Example demonstrating regex functions in DRL.

This example shows how to use regex functions for pattern matching,
text extraction, and data validation.
"""

from drl import interpret

print("=" * 70)
print("DRL Regex Functions Demo")
print("=" * 70)

# Example 1: Validating data formats
print("\n1. Data Validation")
print("-" * 70)

data = {
    "email": "user@example.com",
    "phone": "(555) 123-4567",
    "ssn": "123-45-6789",
}

# Validate email (simple pattern with @ and .)
is_valid_email = interpret(r'regex_search("@", $email)', data)
has_dot = interpret(r'regex_search("\\.", $email)', data)
print(f"Email '{data['email']}' has @ symbol: {is_valid_email}")
print(f"Email '{data['email']}' has dot: {has_dot}")

# Validate phone has area code
has_area_code = interpret(r'regex_search("\\(", $phone)', data)
print(f"Phone '{data['phone']}' has opening paren: {has_area_code}")

# Example 2: Extracting information
print("\n2. Information Extraction")
print("-" * 70)

log_data = {
    "log_entry": "[2024-01-15 10:30:45] ERROR: Database connection failed",
    "product_code": "PROD-12345-XL",
    "message": "Contact support@company.com or call 1-800-555-0199",
}

# Extract date from log using simple pattern
date = interpret(r'regex_extract("\\d{4}-\\d{2}-\\d{2}", $log_entry)', log_data)
print(f"Log date: {date}")

# Extract error level
level = interpret(r'regex_extract("ERROR|WARNING|INFO", $log_entry)', log_data)
print(f"Log level: {level}")

# Extract product number
product_num = interpret(r'regex_extract("PROD-(\\d+)", $product_code, 1)', log_data)
print(f"Product number: {product_num}")

# Extract email (simple pattern)
email = interpret(r'regex_extract("\\w+@\\w+\\.\\w+", $message)', log_data)
print(f"Support email: {email}")

# Example 3: Finding all matches
print("\n3. Finding Multiple Matches")
print("-" * 70)

text_data = {
    "tweet": "Check out #Python #DRL and #RegEx for awesome text processing!",
    "prices": "Items cost $19.99, $5.50, and $125.00",
    "html": "<p>Hello</p> <div>World</div> <span>Test</span>",
}

# Extract all hashtags
hashtags = interpret(r'regex_findall("#\\w+", $tweet)', text_data)
print(f"Hashtags found: {hashtags}")

# Extract all prices
prices = interpret(r'regex_findall("\\$[\\d.]+", $prices)', text_data)
print(f"Prices found: {prices}")

# Extract all HTML tags
tags = interpret(r'regex_findall("<(\\w+)>", $html)', text_data)
print(f"HTML tags found: {tags}")

# Example 4: Text cleaning and transformation
print("\n4. Text Cleaning")
print("-" * 70)

messy_data = {
    "phone_raw": "(555) 123-4567",
    "text": "Hello!!!   World???   How  are   you???",
    "html_text": "<p>This is <b>bold</b> text.</p>",
    "ssn": "123-45-6789",
}

# Clean phone number - remove non-digits
clean_phone = interpret(r'regex_sub("[^\\d]", "", $phone_raw)', messy_data)
print(f"Original: '{messy_data['phone_raw']}'")
print(f"Cleaned:  '{clean_phone}'")

# Normalize whitespace
normalized = interpret(r'regex_sub("\\s+", " ", $text)', messy_data)
print(f"\nOriginal: '{messy_data['text']}'")
print(f"Normalized: '{normalized}'")

# Remove HTML tags
plain_text = interpret(r'regex_sub("<[^>]+>", "", $html_text)', messy_data)
print(f"\nOriginal: '{messy_data['html_text']}'")
print(f"Plain text: '{plain_text}'")

# Mask SSN
masked = interpret(r'regex_sub("\\d", "X", $ssn)', messy_data)
print(f"\nOriginal: '{messy_data['ssn']}'")
print(f"Masked: '{masked}'")

# Example 5: Splitting text
print("\n5. Text Splitting")
print("-" * 70)

split_data = {
    "csv": "apple,banana,cherry",
    "words": "hello   world   test",
    "mixed": "one,two;three|four",
}

# Split CSV
csv_items = interpret(r'regex_split(",", $csv)', split_data)
print(f"CSV split: {csv_items}")

# Split by whitespace (handles multiple spaces)
word_list = interpret(r'regex_split("\\s+", $words)', split_data)
print(f"Words split: {word_list}")

# Split by multiple delimiters
items = interpret(r'regex_split("[,;|]", $mixed)', split_data)
print(f"Mixed delimiters: {items}")

# Example 6: Conditional logic with regex
print("\n6. Conditional Logic with Regex")
print("-" * 70)

users = [
    {"email": "alice@company.com", "username": "alice123"},
    {"email": "invalid-email", "username": "bob!@#"},
    {"email": "charlie@example.org", "username": "charlie_x"},
]

for user in users:
    # Validate email
    email_valid = interpret(r'regex_search("@.*\.", $email)', user)

    # Validate username (alphanumeric and underscore only)
    username_valid = interpret(r'regex_match("^\w+$", $username)', user)

    # Overall validation
    expr = 'if($valid_email and $valid_user, "VALID", "INVALID")'
    status = interpret(expr, {"valid_email": email_valid, "valid_user": username_valid})

    print(f"User: {user['username']:12} Email: {user['email']:25} Status: {status}")

# Example 7: Password validation
print("\n7. Password Strength Validation")
print("-" * 70)

passwords = ["weak", "Better1", "Str0ng!Pass", "MyP@ssw0rd123"]

for pwd in passwords:
    data = {"pwd": pwd}

    # Check various requirements
    has_upper = interpret(r'regex_search("[A-Z]", $pwd)', data)
    has_lower = interpret(r'regex_search("[a-z]", $pwd)', data)
    has_digit = interpret(r'regex_search("\d", $pwd)', data)
    has_special = interpret(r'regex_search("[^a-zA-Z0-9]", $pwd)', data)
    has_length = len(pwd) >= 8

    # Count requirements met
    score = sum([has_upper, has_lower, has_digit, has_special, has_length])

    strength = "Weak" if score < 3 else "Medium" if score < 5 else "Strong"
    print(f"Password: {pwd:15} Score: {score}/5  Strength: {strength}")

# Example 8: Data parsing and extraction
print("\n8. Complex Data Parsing")
print("-" * 70)

server_log = {
    "request": "GET /api/users/12345?filter=active HTTP/1.1",
    "ip_log": "Client IP: 192.168.1.100, Server: 10.0.0.5",
    "timestamp": "Timestamp: 2024-01-15T10:30:45.123Z",
}

# Extract HTTP method
method = interpret(r'regex_extract("^(\w+)\s", $request, 1)', server_log)
print(f"HTTP Method: {method}")

# Extract user ID
user_id = interpret(r'regex_extract("/users/(\d+)", $request, 1)', server_log)
print(f"User ID: {user_id}")

# Extract all IP addresses
ips = interpret(r'regex_findall("\d+\.\d+\.\d+\.\d+", $ip_log)', server_log)
print(f"IP Addresses: {ips}")

# Extract ISO timestamp
timestamp = interpret(
    r'regex_extract("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", $timestamp)', server_log
)
print(f"Timestamp: {timestamp}")

# Example 9: Combining regex with other functions
print("\n9. Combining Regex with Other Functions")
print("-" * 70)

data = {"text": "Prices: $10.50, $25.99, $5.00, $100.00"}

# Extract prices, convert to float, calculate total
prices_str = interpret(r'regex_findall("\$[\d.]+", $text)', data)
print(f"Found prices: {prices_str}")

# Clean and convert (need to do this programmatically in Python)
prices_clean = [float(p.replace("$", "")) for p in prices_str]
total = sum(prices_clean)
print(f"Total: ${total:.2f}")

# Count how many prices
count_expr = r'len(regex_findall("\$[\d.]+", $text))'
count = interpret(count_expr, data)
print(f"Number of prices: {count}")

print("\n" + "=" * 70)
print("All regex examples completed successfully!")
print("=" * 70)
