# drl

[![PyPI - Version](https://img.shields.io/pypi/v/drl.svg)](https://pypi.org/project/drl)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/drl.svg)](https://pypi.org/project/drl)

**Dynamic Reference Language (DRL)** - A powerful expression language for data processing and configuration management.

DRL is a lightweight library that interprets string expressions to extract, process, and transform data from dictionary-like sources. It provides:

- 🔗 **Data References**: Access nested dictionary values with customizable syntax
- 🧮 **Math Operations**: Full arithmetic support with proper operator precedence
- 🔍 **Comparisons & Logic**: Compare values and combine conditions with `and`, `or`, `not`
- ⚙️ **Conditional Logic**: Inline conditionals with the `if()` function
- 📦 **40+ Built-in Functions**: String manipulation, math, random, date/time, and more
- 🎨 **Custom Syntax**: Tailor the syntax to match your preferred style
- 🔧 **Custom Functions**: Extend with your own domain-specific functions
- 📝 **Type Safety**: Automatic type conversion based on function signatures

Perfect for configuration files, template systems, data pipelines, and business rule engines.

-----

## Quick Start

```bash
pip install drl
```

```python
from drl import interpret

# Simple data access
data = {"user": {"name": "Alice", "age": 30}}
print(interpret("$user>name", data))  # "Alice"

# Math and comparisons
print(interpret("$user>age >= 18", data))  # True

# Conditional logic
expr = 'if($user>age >= 18, "adult", "minor")'
print(interpret(expr, data))  # "adult"

# String functions
print(interpret('upper($user>name)', data))  # "ALICE"
```

-----

## Table of Contents

- [Quick Start](#quick-start)
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
- [Available Functions](#available-functions)
- [Installation](#installation)
- [License](#license)

## Usage Examples

### Basic Data Access

```python
import drl
import json

# Load data
source_data = json.load(open("my_file.json"))

# Access nested values
config_item = "print($root>timestamp)"
drl.interpret(config_item, source_data)
# Prints the timestamp value
```

### String Processing

```python
source_data = json.load(open("map_locations.json"))
config_item = "split($houses>Maryland City>occupants, ',')"
people = drl.interpret(config_item, source_data)
# Returns list of occupants
```

### Calculations and Logic

```python
# Calculate discounted price
data = {"price": 100, "discount": 0.2, "quantity": 5}
expr = "($price * (1 - $discount)) * $quantity"
total = drl.interpret(expr, data)
# Returns: 400.0

# Conditional access control
data = {"age": 25, "verified": True}
expr = 'if($age >= 18 and $verified, "access granted", "access denied")'
result = drl.interpret(expr, data)
# Returns: "access granted"
```

### Working with Custom Functions

```python
from drl import DRLConfig, interpret

# Define business logic
def calculate_shipping(weight, zone):
    rates = {"local": 5, "regional": 10, "international": 25}
    return rates.get(zone, 10) + (weight * 0.5)

config = DRLConfig(custom_functions={"shipping": calculate_shipping})

data = {"weight": 3.5, "zone": "regional"}
cost = interpret("shipping($weight, $zone)", data, config)
# Returns: 11.75
```

## Syntax

DRL supports the following language features:

### Data References

Access values from the context dictionary using the reference indicator (`$` by default) followed by keys separated by the key delimiter (`>` by default):

```python
drl.interpret("$root>user>name", {"root": {"user": {"name": "Alice"}}})
# Returns: "Alice"
```

Keys with spaces are supported:

```python
drl.interpret("$user info>full name", {"user info": {"full name": "Bob Smith"}})
# Returns: "Bob Smith"
```

### Mathematical Operators

DRL supports standard mathematical operators with proper precedence:

- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Modulo: `%`
- Power: `^`

```python
drl.interpret("$x + $y * 2", {"x": 10, "y": 5})
# Returns: 20 (following order of operations: 10 + 5*2)

drl.interpret("($x + $y) * 2", {"x": 10, "y": 5})
# Returns: 30 (parentheses override precedence)

drl.interpret("2 ^ 3", {})
# Returns: 8 (exponentiation)
```

### Function Calls

Call built-in functions using function names followed by arguments in parentheses:

```python
drl.interpret('split($data, ",")', {"data": "a,b,c"})
# Returns: ["a", "b", "c"]

drl.interpret("max($x, $y)", {"x": 10, "y": 20})
# Returns: 20
```

Functions can be nested and combined with operators:

```python
drl.interpret("len($name) * 2", {"name": "Alice"})
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
drl.interpret("$age >= 18", {"age": 25})
# Returns: True

drl.interpret("$price < 100", {"price": 150})
# Returns: False

drl.interpret("$user>status == 'active'", {"user": {"status": "active"}})
# Returns: True
```

### Logical Operators

Combine conditions using logical operators:

- `and` - Logical AND
- `or` - Logical OR
- `not` - Logical NOT

```python
drl.interpret("$age >= 18 and $age < 65", {"age": 30})
# Returns: True

drl.interpret("$premium or $quantity >= 10", {"premium": False, "quantity": 15})
# Returns: True

drl.interpret("not $disabled", {"disabled": False})
# Returns: True
```

Logical operators follow proper precedence (`not` > `and` > `or`):

```python
drl.interpret("True or False and False", {})
# Returns: True (evaluated as: True or (False and False))
```

### Conditional Logic

Use the `if()` function for conditional expressions:

```python
drl.interpret('if($score >= 60, "pass", "fail")', {"score": 75})
# Returns: "pass"

# Nested conditions
expr = 'if($score >= 90, "A", if($score >= 80, "B", "C"))'
drl.interpret(expr, {"score": 85})
# Returns: "B"

# Complex conditions
expr = 'if($age >= 18 and $verified, "access granted", "access denied")'
drl.interpret(expr, {"age": 25, "verified": True})
# Returns: "access granted"
```

## Custom Syntax

DRL allows you to customize the syntax by changing the reference indicator and key delimiter symbols using the `DRLConfig` class:

```python
from drl import interpret, DRLConfig

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

Custom syntax works with all DRL features including operators and functions:

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

Extend DRL with your own custom functions for domain-specific operations:

### Basic Usage

```python
from drl import interpret, DRLConfig

# Define custom function
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

# Register via config
config = DRLConfig(custom_functions={'c_to_f': celsius_to_fahrenheit})

result = interpret('c_to_f($temp)', {'temp': 25}, config)
# Returns: 77.0
```

### Using register_function Helper

```python
from drl import register_function, DRLConfig

config = DRLConfig()

# Register function to config
def discount(price, percent):
    return price * (1 - percent/100)

register_function('discount', discount, config)

result = interpret('discount($price, 20)', {'price': 100}, config)
# Returns: 80.0
```

### Register Globally

```python
from drl import register_function, interpret

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
- **Full integration**: Works with all DRL features (operators, conditionals, references)

```python
config = DRLConfig(custom_functions={
    'double': lambda x: x * 2,
    'is_valid': lambda age: 0 < age < 150,
    'clamp': lambda val, min_val, max_val: max(min_val, min(val, max_val))
})

# Use in complex expressions
expr = 'if(is_valid($age), double($age), 0)'
result = interpret(expr, {'age': 30}, config)
# Returns: 60

# Combine with built-in functions
expr = 'max(clamp($value, 0, 100), 50)'
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
expr = 'tax(discount($price, $tier), $tax_rate)'
final_price = interpret(expr, data, config)
# Returns: 91.8 (100 * 0.85 * 1.08)
```

## Available Functions

DRL includes 40+ built-in functions organized by category:

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
drl.interpret(r'regex_search("@.*\\.", $email)', {"email": "user@example.com"})
# Returns: True

# Extract all numbers
drl.interpret(r'regex_findall("\\d+", "a1b22c333")', {})
# Returns: ['1', '22', '333']

# Clean phone number
drl.interpret(r'regex_sub("[^\\d]", "", "(123) 456-7890")', {})
# Returns: '1234567890'

# Extract domain from email
drl.interpret(r'regex_extract("@(\\w+\\.\\w+)", "user@example.com", 1)', {})
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
pip install drl
```

## License

`drl` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
