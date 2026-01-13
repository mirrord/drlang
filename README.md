# DRLang

[![PyPI - Version](https://img.shields.io/pypi/v/drlang.svg)](https://pypi.org/project/drlang)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/drlang.svg)](https://pypi.org/project/drlang)

**Dynamic Reference Language (DRLang)** - A powerful expression language for data processing and configuration management.

DRLang is a lightweight library that interprets string expressions to extract, process, and transform data from dictionary-like sources. It provides:

- 🔗 **Data References**: Three reference types for different behaviors: `$[ref]` optional, `$(ref)` required, `${ref}` literal fallback
- 🧮 **Math Operations**: Full arithmetic support with proper operator precedence
- 🔍 **Comparisons & Logic**: Compare values and combine conditions with `and`, `or`, `not`
- ⚙️ **Conditional Logic**: Inline conditionals with the `if()` function
- 📦 **40+ Built-in Functions**: String manipulation, math, random, date/time, and more
- 🎨 **Custom Syntax**: Tailor the syntax to match your preferred style
- 🔧 **Custom Functions**: Extend with your own domain-specific functions
- 📝 **Type Safety**: Automatic type conversion based on function signatures
- 🐛 **Verbose Error Messages**: Detailed error context with position tracking and helpful suggestions

Perfect for configuration files, template systems, data pipelines, and business rule engines.

-----

## Quick Start

```bash
pip install drlang
```

```python
from drlang import interpret

# Simple data access
data = {"user": {"name": "Alice", "age": 30}}
print(interpret("$user>name", data))  # "Alice"

# Math and comparisons
print(interpret("$user>age >= 18", data))  # True

# Conditional logic
expr = 'if $(user>age >= 18, "adult", "minor")'
print(interpret(expr, data))  # "adult"

# String functions
print(interpret('upper $(user>name)', data))  # "ALICE"
```

### Interactive CLI

Test and debug expressions interactively:

```bash
# Start interactive shell
drlang

# With context data preloaded
drlang -f data.json

# Evaluate single expression
drlang -c '$user>name' -f data.json

# Custom syntax
drlang --ref @ --delim .
```

**Interactive commands:**
- `eval <expr>` - Evaluate expression (or just type the expression)
- `set <key> <json>` - Add context data
- `context` - View current context
- `test <dict>` - Test multiple expressions
- `functions` - List available functions
- `help <function>` - Get function documentation
- `examples` - Show usage examples

-----

## Table of Contents

- [Quick Start](#quick-start)
- [Interactive CLI](#interactive-cli)
- [Usage Examples](#usage-examples)
- [Syntax](#syntax)
  - [Data References](#data-references)
  - [Mathematical Operators](#mathematical-operators)
  - [Comparison Operators](#comparison-operators)
  - [Logical Operators](#logical-operators)
  - [Conditional Logic](#conditional-logic)
  - [Function Calls](#function-calls)
- [Custom Syntax](#custom-syntax)
- [Custom Functions](#custom-functions)
- [Error Handling](#error-handling)
- [Available Functions](#available-functions)
- [Installation](#installation)
- [License](#license)

## Usage Examples

### Basic Data Access

```python
import drlang
import json

# Load data
source_data = json.load(open("my_file.json"))

# Access nested values
config_item = "print $(root>timestamp)"
drlang.interpret(config_item, source_data)
# Prints the timestamp value
```

### String Processing

```python
source_data = json.load(open("map_locations.json"))
config_item = "split $(houses>Maryland City>occupants, ',')"
people = drlang.interpret(config_item, source_data)
# Returns list of occupants
```

### Calculations and Logic

```python
# Calculate discounted price
data = {"price": 100, "discount": 0.2, "quantity": 5}
expr = "$(price * (1 - $discount)) * $quantity"
total = drlang.interpret(expr, data)
# Returns: 400.0

# Conditional access control
data = {"age": 25, "verified": True}
expr = 'if $(age >= 18 and $verified, "access granted", "access denied")'
result = drlang.interpret(expr, data)
# Returns: "access granted"
```

### Working with Custom Functions

```python
from drlang import DRLConfig, interpret

# Define business logic
def calculate_shipping(weight, zone):
    rates = {"local": 5, "regional": 10, "international": 25}
    return rates.get(zone, 10) + (weight * 0.5)

config = DRLConfig(custom_functions={"shipping": calculate_shipping})

data = {"weight": 3.5, "zone": "regional"}
cost = interpret("shipping $(weight, $zone)", data, config)
# Returns: 11.75
```

## Interactive CLI

DRLang includes a powerful command-line interface for testing expressions, debugging, and exploring functions.

### Quick Start

```bash
# Start interactive shell
drlang

# With context data preloaded
drlang -f data.json

# Evaluate single expression
drlang -c '$user>name' -f data.json

# Custom syntax
drlang --ref @ --delim .
```

### Interactive Commands

Once in the shell, you can use these commands:

**Expression Evaluation:**
```
drlang> $user>name
=> 'Alice'

drlang> $user>age * 2
=> 60

drlang> if($user>age >= 18, "adult", "minor")
=> 'adult'
```

**Context Management:**
```
drlang> set user {"name": "Alice", "age": 30}
Set user = {'name': 'Alice', 'age': 30}

drlang> context
Current context:
{
  "user": {"name": "Alice", "age": 30}
}

drlang> context load data.json
Loaded context from data.json

drlang> context clear
Context cleared
```

**Batch Testing:**
```
drlang> test {"name": "$user>name", "adult": "$user>age >= 18"}
Testing expressions:
======================================================================
name                 $user>name                    => 'Alice'
adult                $user>age >= 18               => True
======================================================================

drlang> test file expressions.json
(Tests all expressions from the JSON file)
```

**Function Discovery:**
```
drlang> functions
Available functions (40):

String:
  • split  • upper  • lower  • capitalize  • strip  • replace

Math:
  • max  • min  • int  • float  • abs  • round
...

drlang> functions regex
Available functions (6):
Regex:
  • regex_search  • regex_match  • regex_findall
  • regex_sub  • regex_split  • regex_extract

drlang> help split
Function: split
======================================================================
Signature: split(sep=None, maxsplit=-1)

Split string by separator...
```

**Configuration:**
```
drlang> config set @ .
Set custom config: @ and .

drlang> @user.name
=> 'Alice'

drlang> config reset
Reset to default config ($ and >)
```

### Command-Line Options

```bash
# Evaluate expression and exit
drlang -c 'upper("hello")'
# Output: HELLO

# With context file
drlang -f data.json -c '$user>email'
# Output: alice@example.com

# Custom syntax
drlang --ref @ --delim . -c '@user.name' -f data.json

# Show help
drlang --help
```

### Batch Testing with Files

Create `expressions.json`:
```json
{
  "user_name": "$user>name",
  "is_adult": "$user>age >= 18",
  "greeting": "upper($user>name)"
}
```

Test all expressions:
```bash
drlang -f data.json
drlang> test file expressions.json
```

Or programmatically:
```python
from drlang import interpret_dict
import json

with open('data.json') as f:
    context = json.load(f)
with open('expressions.json') as f:
    expressions = json.load(f)

results = interpret_dict(expressions, context)
```

## Syntax

DRLang supports the following language features:

### Data References

DRLang supports three types of data references, each with different behavior when a key is missing:

#### Optional References `$[ref]`

Optional references return `None` when a key is missing instead of raising an error. This enables safe navigation and default value patterns:

```python
data = {"user": {"name": "Alice"}}

# Returns "Alice" when key exists
drlang.interpret("$[user>name]", data)
# Returns: "Alice"

# Returns None when key is missing (no error)
drlang.interpret("$[user>age]", data)
# Returns: None

# Safe navigation through missing paths
drlang.interpret("$[user>profile>bio]", data)
# Returns: None
```

**Use cases for optional references:**
- Providing default values: `if($[user>age], $[user>age], 18)`
- Safe navigation: Check if paths exist without errors
- Optional configuration: `if($[config>debug], "debug mode", "production")`

#### Required References `$(ref)`

Required references raise a `DRLReferenceError` when a key is missing. Use these for mandatory data that must exist:

```python
data = {"config": {"api_key": "secret123"}}

# Returns value when key exists
drlang.interpret("$(config>api_key)", data)
# Returns: "secret123"

# Raises DRLReferenceError when key is missing
drlang.interpret("$(config>database_url)", data)
# Raises: DRLReferenceError
```

**Use cases for required references:**
- Validating critical configuration exists
- Ensuring mandatory fields are present
- Failing fast when required data is missing

#### Literal Fallback References `${ref}`

Literal references return the original reference string when a key is missing. This is useful for template strings where you want to preserve placeholders:

```python
data = {"user": {"name": "Bob"}}

# Returns value when key exists
drlang.interpret("${user>name}", data)
# Returns: "Bob"

# Returns the reference string when key is missing
drlang.interpret("${user>age}", data)
# Returns: "$user>age"

# Template example
drlang.interpret('"${user>name} is(${user>age} years old"', data)
# Returns: "Bob is $user>age years old"
```

**Use cases for literal fallback:**
- Template strings where missing values should remain as placeholders
- Configuration files that may be partially filled
- Debugging (see which references are missing)

#### Mixed References

Combine different reference types in the same expression:

```python
data = {"user": {"name": "Bob"}}

# Check with optional, access with required
expr = 'if($[user>verified], ($user>name), "unverified")'
drlang.interpret(expr, data)
# Returns: "unverified" (verified is optional, doesn't exist)
```

#### Keys with Spaces

All reference types support keys containing spaces:

```python
drlang.interpret("$[user info>full name]", {"user info": {"full name": "Bob Smith"}})
# Returns: "Bob Smith"

drlang.interpret("$(company name)", {"company name": "ACME Corp"})
# Returns: "ACME Corp"

drlang.interpret("${missing key}", {})
# Returns: "$missing key"
```

### Mathematical Operators

DRLang supports standard mathematical operators with proper precedence:

- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Modulo: `%`
- Power: `^`

```python
drlang.interpret("$x + $y * 2", {"x": 10, "y": 5})
# Returns: 20 (following order of operations: 10 + 5*2)

drlang.interpret("$(x + $y) * 2", {"x": 10, "y": 5})
# Returns: 30 (parentheses override precedence)

drlang.interpret("2 ^ 3", {})
# Returns: 8 (exponentiation)
```

### Function Calls

Call built-in functions using function names followed by arguments in parentheses:

```python
drlang.interpret('split $(data, ",")', {"data": "a,b,c"})
# Returns: ["a", "b", "c"]

drlang.interpret("max $(x, $y)", {"x": 10, "y": 20})
# Returns: 20
```

Functions can be nested and combined with operators:

```python
drlang.interpret("len $(name) * 2", {"name": "Alice"})
# Returns: 10 (len("Alice") = 5, 5 * 2 = 10)
```

### Comparison Operators

Compare values using standard comparison operators:

- Equal: `==`
- Not equal: `!=`
- Less than: `<`
- Greater than: `>`
- Less than or equal: `<=`
- Greater than or equal: `>=`

```python
drlang.interpret("$age >= 18", {"age": 25})
# Returns: True

drlang.interpret("$price < 100", {"price": 150})
# Returns: False

drlang.interpret("$user>status == 'active'", {"user": {"status": "active"}})
# Returns: True
```

### Logical Operators

Combine conditions using logical operators:

- `and` - Logical AND
- `or` - Logical OR
- `not` - Logical NOT

```python
drlang.interpret("$age >= 18 and $age < 65", {"age": 30})
# Returns: True

drlang.interpret("$premium or $quantity >= 10", {"premium": False, "quantity": 15})
# Returns: True

drlang.interpret("not $disabled", {"disabled": False})
# Returns: True
```

Logical operators follow proper precedence (`not` > `and` > `or`):

```python
drlang.interpret("True or False and False", {})
# Returns: True (evaluated as: True or (False and False))
```

### Conditional Logic

Use the `if()` function for conditional expressions:

```python
drlang.interpret('if $(score >= 60, "pass", "fail")', {"score": 75})
# Returns: "pass"

# Nested conditions
expr = 'if $(score >= 90, "A", if($score >= 80, "B", "C"))'
drlang.interpret(expr, {"score": 85})
# Returns: "B"

# Complex conditions
expr = 'if $(age >= 18 and $verified, "access granted", "access denied")'
drlang.interpret(expr, {"age": 25, "verified": True})
# Returns: "access granted"
```

## Custom Syntax

DRLang allows you to customize the syntax by changing the reference indicator and key delimiter symbols using the `DRLConfig` class:

```python
from drlang import interpret, DRLConfig

# JavaScript-style syntax with @ and .
config = DRLConfig('@', '.')
interpret('@user.name', {'user': {'name': 'Alice'}}, config)
# Returns: "Alice"

# Path-style syntax with # and /
config = DRLConfig('#', '/')
interpret('#root/path/to/value', {'root': {'path': {'to': {'value': 42}}}}, config)
# Returns: 42

# C++-style syntax with & and ::
config = DRLConfig('&', '::')
interpret('&namespace::class::method', {'namespace': {'class': {'method': 'result'}}}, config)
# Returns: "result"
```

Custom syntax works with all DRLang features including operators and functions:

```python
config = DRLConfig('@', '.')
interpret('(@price * 1.1) - @discount', {'price': 100, 'discount': 10}, config)
# Returns: 100.0

interpret('split(@data.items, ",")', {'data': {'items': 'x,y,z'}}, config)
# Returns: ['x', 'y', 'z']
```

### Restrictions

- Reference indicators cannot be: `(`, `)`, `,`, `'`, `"`, or whitespace
- Key delimiters cannot be: `(`, `)`, `,`, `'`, `"`, or whitespace
- The default syntax is `$` for references and `>` for key delimiters

## Custom Functions

Extend DRLang with your own custom functions for domain-specific operations:

### Basic Usage

```python
from drlang import interpret, DRLConfig

# Define custom function
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

# Register via config
config = DRLConfig(custom_functions={'c_to_f': celsius_to_fahrenheit})

result = interpret('c_to_f $(temp)', {'temp': 25}, config)
# Returns: 77.0
```

### Using register_function Helper

```python
from drlang import register_function, DRLConfig

config = DRLConfig()

# Register function to config
def discount(price, percent):
    return price * (1 - percent/100)

register_function('discount', discount, config)

result = interpret('discount $(price, 20)', {'price': 100}, config)
# Returns: 80.0
```

### Register Globally

```python
from drlang import register_function, interpret

# Register globally (available without config)
register_function('square', lambda x: x * x)

result = interpret('square(7)', {})
# Returns: 49
```

### Custom Functions Features

- **Lambda functions**: Use inline lambdas for simple operations
- **Multiple arguments**: Support for any number of parameters
- **Type conversion**: Automatic type conversion based on type hints
- **Override built-ins**: Custom functions take precedence over built-in ones
- **Full integration**: Works with all ang features (operators, conditionals, references)

```python
config = DRLConfig(custom_functions={
    'double': lambda x: x * 2,
    'is_valid': lambda age: 0 < age < 150,
    'clamp': lambda val, min_val, max_val: max(min_val, min(val, max_val))
})

# Use in complex expressions
expr = 'if(is_valid $(age), double $(age), 0)'
result = interpret(expr, {'age': 30}, config)
# Returns: 60

# Combine with built-in functions
expr = 'max(clamp $(value, 0, 100), 50)'
result = interpret(expr, {'value': 150}, config)
# Returns: 100
```

### Real-World Example

```python
def calculate_tax(price, tax_rate):
    return price * (1 + tax_rate)

def apply_discount(price, customer_tier):
    discounts = {'bronze': 0.05, 'silver': 0.10, 'gold': 0.15}
    return price * (1 - discounts.get(customer_tier, 0))

config = DRLConfig(custom_functions={
    'tax': calculate_tax,
    'discount': apply_discount
})

# Calculate final price
data = {'price': 100, 'tier': 'gold', 'tax_rate': 0.08}
expr = 'tax(discount $(price, $tier), $tax_rate)'
final_price = interpret(expr, data, config)
# Returns: 91.8 (100 * 0.85 * 1.08)
```

## Error Handling

DRLang provides detailed, actionable error messages that show exactly where and how parsing failed. The error messages include:

- **Position tracking**: Shows the exact location of the error in your expression
- **Visual pointer**: A caret (^) highlights the problematic position
- **Helpful context**: Suggestions and available options to fix the issue
- **Error categories**: Specific exception types for different error scenarios

### Exception Types

```python
from drlang import (
    DRLError,           # Base exception class
    DRLSyntaxError,     # Syntax errors during parsing
    DRLReferenceError,  # Reference path not found
    DRLNameError,       # Function not found
    DRLTypeError        # Type-related errors
)
```

### Example Error Messages

**Missing reference key:**
```python
try:
    interpret("$user>age", {"user": {"name": "Alice"}})
except DRLReferenceError as e:
    print(e)
```

Output:
```
Reference key 'age' not found in context

  Expression: $user>age
  Context: Failed at: user>age
  Available keys: ['name']
```

**Unterminated string:**
```python
try:
    interpret('split $(data, "comma)', {"data": "a,b,c"})
except DRLSyntaxError as e:
    print(e)
```

Output:
```
Unterminated string literal starting with "

  Expression: split $(data, "comma)
  Position 13:
    split $(data, "comma)
                 ^
  Context: String started at position 13 but never closed
```

**Undefined function:**
```python
try:
    interpret("unknown_func(5)", {})
except DRLNameError as e:
    print(e)
```

Output:
```
Function 'unknown_func' not found

  Expression: unknown_func(5)
  Context: Function 'unknown_func' is not defined. Check spelling or register as custom function.
```

**Type error:**
```python
try:
    interpret("$config>setting", {"config": "string value"})
except DRLTypeError as e:
    print(e)
```

Output:
```
Cannot navigate into non-dict value at key 'setting'

  Expression: $config>setting
  Context: Value at 'config' is str, not a dictionary
```

**Division by zero:**
```python
try:
    interpret("100 / (5 - 5)", {})
except DRLTypeError as e:
    print(e)
```

Output:
```
Division by zero

  Expression: 100 / (5 - 5)
  Context: Cannot divide by zero
```

### Best Practices

1. **Catch specific exceptions** for targeted error handling
2. **Display error messages to users** for debugging configuration files
3. **Validate expressions** before runtime when possible
4. **Use try-except blocks** around interpret() calls in production

```python
from drlang import interpret, DRLError

def safe_interpret(expression, context):
    try:
        return interpret(expression, context)
    except DRLError as e:
        # Log the detailed error message
        print(f"DRL Error: {e}")
        return None  # or a default value
```

See [examples/error_demo.py](examples/error_demo.py) for a comprehensive demonstration of error messages.

## Available Functions

DRLang includes 40+ built-in functions organized by category:

### Conditional Functions
- `if(condition, true_value, false_value)` - Conditional expression

### String Functions
- `split(string, separator)` - Split string by separator
- `upper(string)` - Convert to uppercase
- `lower(string)` - Convert to lowercase
- `capitalize(string)` - Capitalize first letter
- `replace(string, old, new)` - Replace occurrences
- `strip(string)` - Remove leading/trailing whitespace
- `find(string, substring)` - Find substring position
- `join(separator, iterable)` - Join elements with separator

### Regex Functions
- `regex_search(pattern, string)` - Check if pattern exists in string (returns bool)
- `regex_match(pattern, string)` - Check if string starts with pattern (returns bool)
- `regex_findall(pattern, string)` - Find all matches (returns list)
- `regex_sub(pattern, replacement, string)` - Replace all pattern matches
- `regex_split(pattern, string)` - Split string by pattern (returns list)
- `regex_extract(pattern, string, group=0)` - Extract first match or capture group

```python
# Validate email format
drlang.interpret(r'regex_search("@.*\\.", $email)', {"email": "user@example.com"})
# Returns: True

# Extract all numbers
drlang.interpret(r'regex_findall("\\d+", "a1b22c333")', {})
# Returns: ['1', '22', '333']

# Clean phone number
drlang.interpret(r'regex_sub("[^\\d]", "", "(123) 456-7890")', {})
# Returns: '1234567890'

# Extract domain from email
drlang.interpret(r'regex_extract("@(\\w+\\.\\w+)", "user@example.com", 1)', {})
# Returns: 'example.com'
```

### Math Functions
- `max(*values)` - Return maximum value
- `min(*values)` - Return minimum value
- `add(*values)` - Sum all values
- `int(value)` - Convert to integer
- `float(value)` - Convert to float

### Type Conversion
- `int(value)` - Convert to integer
- `float(value)` - Convert to float
- `str(value)` - Convert to string
- `bool(value)` - Convert to boolean

### Collection Functions
- `len(collection)` - Get length
- `all(iterable)` - True if all elements are truthy
- `any(iterable)` - True if any element is truthy

### Random Functions
- `random()` - Random float [0, 1)
- `randint(a, b)` - Random integer [a, b]
- `uniform(a, b)` - Random float [a, b]
- `randrange(start, stop)` - Random int from range
- `choice(sequence)` - Random element
- `shuffle(sequence)` - Shuffle sequence in place

### Date/Time Functions
- `datetime(...)` - Create datetime object
- `date(...)` - Create date object
- `time(...)` - Create time object
- `timedelta(...)` - Create timedelta object
- `strptime(string, format)` - Parse datetime string
- `strftime(format, datetime)` - Format datetime

### I/O Functions
- `print(*values)` - Print to stdout

Functions automatically convert argument types based on type hints.

## Installation

```console
pip install drlang
```

## License

`drlang` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
