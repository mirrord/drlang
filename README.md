# DRLang

[![PyPI - Version](https://img.shields.io/pypi/v/drlang.svg)](https://pypi.org/project/drlang)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/drlang.svg)](https://pypi.org/project/drlang)

**Dynamic Reference Language (DRLang)** - A powerful string templating and expression language for data processing and configuration management.

DRLang provides `interpolate()` and `interpolate_dict()` functions for processing template strings with embedded references and expressions. Templates are **literal by default** - only content marked with `$references` or `{% expression blocks %}` is evaluated.

**Key Features:**
- 📝 **String Interpolation**: `interpolate()` for single templates, `interpolate_dict()` for batch processing
- 🔒 **Type Preservation**: Single references preserve original types (int, float, bool, list, dict)
- 🎯 **Type-Preserving Expressions**: `{%= %}` blocks preserve native types when used alone
- 🔗 **Data References**: Three types: `$[ref]` optional, `$(ref)` required, `${ref}` literal fallback
- 🔄 **Nested References**: Dynamic key resolution with `$(outer>$(inner)>path)` syntax
- 🧮 **Expression Blocks**: Full expression evaluation in `{% %}` blocks
- 📦 **40+ Built-in Functions**: String manipulation, math, random, date/time, regex, and more
- 🎨 **Custom Syntax**: Tailor reference indicators and key delimiters to your style
- 🔧 **Custom Functions**: Extend with your own domain-specific functions
- 🐛 **Verbose Errors**: Detailed error context with position tracking and helpful suggestions

Perfect for configuration files, template systems, data pipelines, and business rule engines.

-----

## Quick Start

```bash
pip install drlang
```

```python
from drlang import interpolate, interpolate_dict

# Simple template interpolation
data = {"user": {"name": "Alice", "age": 30}}
print(interpolate("Hello $user>name!", data))  # "Hello Alice!"

# Type preservation - single references preserve their type
print(interpolate("$user>age", data))  # 30 (int, not string)

# Type-preserving expressions - use {%= %} to keep native types
print(interpolate("{%= 5 + 10 %}", {}))  # 15 (int, not string)

# Expression blocks for calculations
print(interpolate("Age in months: {% $user>age * 12 %}", data))  # "Age in months: 360"

# Batch processing multiple templates
templates = {
    "greeting": "Hello $user>name!",
    "is_adult": "{% $user>age >= 18 %}",
    "status": "{% if($user>age >= 18, 'adult', 'minor') %}"
}
results = interpolate_dict(templates, data)
# {'greeting': 'Hello Alice!', 'is_adult': 'True', 'status': 'adult'}
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
- [String Interpolation](#string-interpolation)
- [Batch Processing with interpolate_dict](#batch-processing-with-interpolate_dict)
- [Low-Level Expression Evaluation](#low-level-expression-evaluation)
- [Syntax](#syntax)
  - [Data References](#data-references)
  - [Mathematical Operators](#mathematical-operators)
  - [Comparison Operators](#comparison-operators)
  - [Logical Operators](#logical-operators)
  - [Conditional Logic](#conditional-logic)
  - [List Operations](#list-operations)
  - [Function Calls](#function-calls)
- [Custom Syntax](#custom-syntax)
- [Custom Functions](#custom-functions)
- [Error Handling](#error-handling)
- [Available Functions](#available-functions)
- [Installation](#installation)
- [License](#license)

## Usage Examples

### Basic Template Interpolation

```python
from drlang import interpolate, interpolate_dict
import json

# Load data
with open("config.json") as f:
    context = json.load(f)

# Simple template with reference
result = interpolate("Server: $server>host:{% $server>port %}", context)
# "Server: localhost:8080"

# URL construction (bare refs stop at /)
result = interpolate("https://$domain/api/v1/users/$user_id", 
                     {"domain": "api.example.com", "user_id": "123"})
# "https://api.example.com/api/v1/users/123"
```

### String Processing

```python
from drlang import interpolate

data = {"names": "alice,bob,charlie"}

# Use expression blocks for function calls
result = interpolate("Users: {% split($names, ',') %}", data)
# "Users: ['alice', 'bob', 'charlie']"

# Transform data
result = interpolate("{% upper($names) %}", data)
# "ALICE,BOB,CHARLIE"
```

### Calculations and Conditional Logic

```python
from drlang import interpolate

# Calculate discounted price
data = {"price": 100, "discount": 0.2, "quantity": 5}
result = interpolate("Total: ${% ($price * (1 - $discount)) * $quantity %}", data)
# "Total: $400.0"

# Conditional content
data = {"age": 25, "verified": True}
result = interpolate("Status: {% if($age >= 18 and $verified, 'access granted', 'access denied') %}", data)
# "Status: access granted"
```

### Batch Processing with interpolate_dict

```python
from drlang import interpolate_dict, DRLConfig

templates = {
    "greeting": "Hello $user>name!",
    "summary": "You have {% $items %} items worth ${% $total %}",
    "nested": {
        "email": "Contact: $user>email",
        "phone": "$[user>phone]"  # Optional - empty string if missing
    }
}

context = {
    "user": {"name": "Alice", "email": "alice@example.com"},
    "items": 5,
    "total": 99.99
}

# Process all templates at once
results = interpolate_dict(templates, context)

# With drop_empty=True, exclude keys with empty values
config = DRLConfig(drop_empty=True)
results = interpolate_dict(templates, context, config)
```

### Working with Custom Functions

```python
from drlang import interpolate, DRLConfig

# Define business logic
def calculate_shipping(weight, zone):
    rates = {"local": 5, "regional": 10, "international": 25}
    return rates.get(zone, 10) + (weight * 0.5)

config = DRLConfig(custom_functions={"shipping": calculate_shipping})

data = {"weight": 3.5, "zone": "regional"}
result = interpolate("Shipping cost: ${% shipping($weight, $zone) %}", data, config)
# "Shipping cost: $11.75"
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
from drlang import interpolate_dict, DRLConfig
import json

with open('data.json') as f:
    context = json.load(f)
with open('templates.json') as f:
    templates = json.load(f)

# Default: includes all keys (even with None values)
results = interpolate_dict(templates, context)

# With drop_empty=True: excludes keys with None values
config = DRLConfig(drop_empty=True)
results = interpolate_dict(templates, context, config)
```

See [Batch Processing with interpolate_dict](#batch-processing-with-interpolate_dict) for more details on filtering None values.

## Syntax

DRLang supports the following language features. These features can be used in two ways:

1. **In `{% %}` expression blocks** within `interpolate()` templates:
   ```python
   interpolate("Result: {% $x + $y * 2 %}", {"x": 10, "y": 5})  # "Result: 20"
   ```

2. **Directly with `interpret()`** for raw expression evaluation:
   ```python
   interpret("$x + $y * 2", {"x": 10, "y": 5})  # 20
   ```

The examples below use `interpret()` to show the raw expression results. In templates, wrap these expressions in `{% %}` blocks.

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

#### Keys with Special Characters

DRLang supports keys containing spaces, parentheses, brackets, and other special characters. The behavior differs between **bare references** and **bracketed references**:

**Bare References** (`$ref`) - Stop at spaces and common delimiters. Best for simple identifiers:

```python
# Simple keys work with bare references
drlang.interpret("$name", {"name": "Alice"})
# Returns: "Alice"

# Keys with spaces work in interpret() - spaces allowed until operators/functions
drlang.interpret("$user name", {"user name": "Bob"})
# Returns: "Bob"
```

**Bracketed References** - Use `$(...)`, `$[...]`, or `${...}` for keys containing special characters:

```python
# Keys with spaces (recommended for clarity)
drlang.interpret("$(user info>full name)", {"user info": {"full name": "Bob Smith"}})
# Returns: "Bob Smith"

# Keys with parentheses (MUST use bracketed syntax)
drlang.interpret("$(getData())", {"getData()": 42})
# Returns: 42

# Keys with nested parentheses - balanced delimiter parsing
drlang.interpret("$(func(a(b)))", {"func(a(b))": "nested"})
# Returns: "nested"

# Optional reference with special characters
drlang.interpret("$[method()]", {"method()": "result"})
# Returns: "result"

# Passthrough reference with special characters  
drlang.interpret("${missing()}", {})
# Returns: "$missing()"

# Complex nested paths with special characters
data = {"API Response": {"getData()": {"user info": "value"}}}
drlang.interpret("$(API Response>getData()>user info)", data)
# Returns: "value"
```

**In `interpolate()` templates**, bare references stop at spaces and `/` for URL compatibility:

```python
from drlang import interpolate

# Bare refs stop at spaces - use for simple identifiers
interpolate("Hello $name!", {"name": "Alice"})  # "Hello Alice!"

# URL-style templates work naturally  
interpolate("https://$domain/api/v1", {"domain": "example.com"})
# "https://example.com/api/v1"

# For keys with spaces in templates, use bracketed syntax
interpolate("Hello $(user name)!", {"user name": "Bob"})  # "Hello Bob!"

# For keys with parentheses, bracketed syntax is required
interpolate("Result: $(getValue())", {"getValue()": 42})  # "Result: 42"
```

#### Nested References

DRLang supports **nested references** where inner references are resolved first and their values are substituted into the outer reference path. This enables dynamic key selection and powerful data access patterns:

```python
data = {
    "rocks": {
        "mica": {"color": "silver", "hardness": 2.5},
        "granite": {"color": "gray", "hardness": 6.5},
    },
    "records": {"best_rock": "mica"}
}

# First resolves $(records>best_rock) → "mica"
# Then resolves $(rocks>mica>color) → "silver"
drlang.interpret("$(rocks>$(records>best_rock)>color)", data)
# Returns: "silver"
```

**Multiple nested references in one path:**

```python
data = {
    "database": {
        "users_table": {
            "row_5": {"name": "John", "age": 30},
            "row_10": {"name": "Jane", "age": 25}
        }
    },
    "pointers": {"table_name": "users_table", "row_id": "row_10"}
}

# Resolves both nested references dynamically
drlang.interpret("$(database>$(pointers>table_name)>$(pointers>row_id)>name)", data)
# Returns: "Jane"
```

**Deeply nested references (nested within nested):**

```python
data = {
    "data": {
        "item1": {"value": "found it!"},
        "item2": {"value": "something else"}
    },
    "keys": {"k1": "k2", "k2": "k3", "k3": "item1"}
}

# Resolves innermost first, working outward:
# $(keys>k1) → "k2"
# $(keys>k2) → "k3"
# $(keys>k3) → "item1"
# $(data>item1>value) → "found it!"
drlang.interpret("$(data>$(keys>$(keys>$(keys>k1)))>value)", data)
# Returns: "found it!"
```

**Nested references in string interpolation:**

```python
from drlang import interpolate

data = {
    "products": {
        "laptop": {"name": "Pro Laptop", "price": 1299},
        "mouse": {"name": "Wireless Mouse", "price": 29}
    },
    "cart": {"selected_item": "laptop"}
}

interpolate(
    "Product: $(products>$(cart>selected_item)>name), Price: $$(products>$(cart>selected_item)>price)",
    data
)
# Returns: "Product: Pro Laptop, Price: $1299"
```

**Real-world use case - Environment-based configuration:**

```python
data = {
    "config": {
        "dev": {"db_host": "localhost", "api_url": "http://localhost:3000"},
        "prod": {"db_host": "prod.example.com", "api_url": "https://api.example.com"}
    },
    "environment": {"current": "prod"}
}

# Dynamically access config based on current environment
drlang.interpret("$(config>$(environment>current)>db_host)", data)
# Returns: "prod.example.com"
```

**Nested references with all reference behaviors:**

Nested references work with all three reference types:
- **Required** `$(...)`  - Inner/outer references raise errors if missing
- **Optional** `$[...]` - Returns `None` if any reference in the chain is missing
- **Passthrough** `${...}` - Returns original string if missing

```python
data = {
    "users": {"alice": {"email": "alice@example.com"}},
    "session": {"user_id": "bob"}  # bob doesn't exist
}

# Optional nested reference - no error, returns empty string
interpolate("Email: $[users>$(session>user_id)>email]", data)
# Returns: "Email: "

# Required nested reference - would raise DRLReferenceError
# interpolate("Email: $(users>$(session>user_id)>email)", data)  # Error!
```

**Key features:**
- ✅ Supports unlimited nesting depth (up to 100 levels for safety)
- ✅ Works with custom syntax via `DRLConfig`
- ✅ Compatible with all three reference behaviors
- ✅ Works in both `interpret()` and `interpolate()`
- ✅ Can be used with mathematical operations and functions

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

### List Operations

DRLang provides comprehensive support for working with lists, including direct indexing, manipulation functions, and functional programming operations.

#### List Indexing

Access list elements directly through references using integer indices:

```python
data = {"items": ["apple", "banana", "cherry"]}

# Access by index
drlang.interpret("$items>0", data)
# Returns: "apple"

drlang.interpret("$items>2", data)
# Returns: "cherry"
```

**Nested lists:**

```python
data = {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}

# Navigate nested structure
drlang.interpret("$matrix>1>1", data)
# Returns: 5

drlang.interpret("$matrix>0>2", data)
# Returns: 3
```

**Mixed dictionaries and lists:**

```python
data = {
    "users": [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
}

drlang.interpret("$users>0>name", data)
# Returns: "Alice"

drlang.interpret("$users>1>age", data)
# Returns: 25
```

**Negative indices** (using variables to avoid parser issues):

```python
data = {"items": ["a", "b", "c"], "last": -1}

# Use list_get function for negative indices
drlang.interpret("list_get($items, $last)", data)
# Returns: "c"
```

#### List Manipulation Functions

DRLang includes 9 functions for working with lists:

**list_get(list, index, default=None)** - Safe element access:

```python
data = {"nums": [1, 2, 3, 4, 5]}

drlang.interpret("list_get($nums, 2)", data)
# Returns: 3

drlang.interpret("list_get($nums, 10, 'N/A')", data)
# Returns: "N/A"
```

**list_slice(list, start, end, step=1)** - Extract subsequence:

```python
drlang.interpret("list_slice($nums, 1, 4)", data)
# Returns: [2, 3, 4]

drlang.interpret("list_slice($nums, 0, 5, 2)", data)
# Returns: [1, 3, 5]
```

**list_append(list, item)** - Add element (returns new list):

```python
drlang.interpret("list_append($nums, 6)", data)
# Returns: [1, 2, 3, 4, 5, 6]
```

**list_concat(list1, list2)** - Merge lists:

```python
data = {"nums": [1, 2, 3], "more": [4, 5, 6]}
drlang.interpret("list_concat($nums, $more)", data)
# Returns: [1, 2, 3, 4, 5, 6]
```

**list_contains(list, item)** - Check membership:

```python
drlang.interpret("list_contains($nums, 3)", data)
# Returns: True

drlang.interpret("list_contains($nums, 10)", data)
# Returns: False
```

**list_index(list, item, default=None)** - Find position:

```python
drlang.interpret("list_index($nums, 4)", data)
# Returns: 3

data["not_found"] = -1
drlang.interpret("list_index($nums, 99, $not_found)", data)
# Returns: -1
```

**list_reverse(list)** - Reverse order:

```python
drlang.interpret("list_reverse($nums)", data)
# Returns: [5, 4, 3, 2, 1]
```

**list_unique(list)** - Remove duplicates:

```python
data = {"dupes": [1, 2, 2, 3, 1, 4, 3]}
drlang.interpret("list_unique($dupes)", data)
# Returns: [1, 2, 3, 4]
```

**list_flatten(list)** - Flatten one level:

```python
data = {"nested": [[1, 2], [3, 4], [5]]}
drlang.interpret("list_flatten($nested)", data)
# Returns: [1, 2, 3, 4, 5]
```

#### Iteration Functions

DRLang provides powerful functional programming operations for transforming lists. These functions use special variables `$item` (current element) and `$index` (position) within their expressions.

**map(expression, list)** - Transform each element:

```python
data = {"nums": [1, 2, 3, 4]}

# Double each number
drlang.interpret('map("$item * 2", $nums)', data)
# Returns: [2, 4, 6, 8]

# Uppercase strings
data = {"words": ["hello", "world"]}
drlang.interpret('map("upper($item)", $words)', data)
# Returns: ["HELLO", "WORLD"]

# Using index
data = {"nums": [10, 20, 30]}
drlang.interpret('map("$item + $index", $nums)', data)
# Returns: [10, 21, 32]  # (10+0, 20+1, 30+2)

# Complex expressions
data = {"nums": [1, 2, 3, 4, 5]}
expr = 'map("if($item > 3, $item * 10, $item)", $nums)'
drlang.interpret(expr, data)
# Returns: [1, 2, 3, 40, 50]
```

**filter(expression, list)** - Select elements:

```python
data = {"nums": [1, 2, 3, 4, 5, 6]}

# Filter by value
drlang.interpret('filter("$item > 3", $nums)', data)
# Returns: [4, 5, 6]

# Filter even numbers
drlang.interpret('filter("$item % 2 == 0", $nums)', data)
# Returns: [2, 4, 6]

# Filter by index (even positions)
drlang.interpret('filter("$index % 2 == 0", $nums)', data)
# Returns: [1, 3, 5]

# Filter strings
data = {"words": ["apple", "banana", "apricot", "cherry"]}
drlang.interpret('filter("regex_match($item, \"^a\")", $words)', data)
# Returns: ["apple", "apricot"]
```

**reduce(expression, list, initial=None)** - Accumulate to single value:

```python
data = {"nums": [1, 2, 3, 4, 5]}

# Sum all numbers (uses $acc for accumulator)
drlang.interpret('reduce("$acc + $item", $nums)', data)
# Returns: 15

# With initial value
drlang.interpret('reduce("$acc + $item", $nums, 10)', data)
# Returns: 25

# Find maximum
expr = 'reduce("if($item > $acc, $item, $acc)", $nums)'
drlang.interpret(expr, data)
# Returns: 5

# String concatenation
data = {"words": ["Hello", "World", "DRLang"]}
drlang.interpret('reduce("$acc + \" \" + $item", $words)', data)
# Returns: "Hello World DRLang"
```

#### Chaining Operations

Combine multiple list operations for powerful data transformations:

```python
data = {"nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

# Pipeline: double → filter > 10 → sum
doubled = drlang.interpret('map("$item * 2", $nums)', data)
data["doubled"] = doubled

filtered = drlang.interpret('filter("$item > 10", $doubled)', data)
data["filtered"] = filtered

total = drlang.interpret('reduce("$acc + $item", $filtered)', data)
# total = 80 (sum of [12, 14, 16, 18, 20])
```

**Real-world example - Process user data:**

```python
data = {
    "users": [
        {"name": "Alice", "age": 30, "score": 85},
        {"name": "Bob", "age": 25, "score": 92},
        {"name": "Charlie", "age": 35, "score": 78},
        {"name": "Diana", "age": 28, "score": 95}
    ]
}

# Extract names using map
from drlang.functions import map_list
names = map_list("$item>name", data["users"], {})
# Returns: ["Alice", "Bob", "Charlie", "Diana"]

# Filter high scorers
from drlang.functions import filter_list
high_scorers = filter_list("$item>score >= 90", data["users"], {})
# Returns: [{"name": "Bob", ...}, {"name": "Diana", ...}]

# Calculate average score
from drlang.functions import reduce_list
scores = map_list("$item>score", data["users"], {})
total = reduce_list("$acc + $item", scores, 0, {})
average = total / len(scores)
# average = 87.5
```

See [examples/list_operations_demo.py](examples/list_operations_demo.py) for more comprehensive examples.

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

## String Interpolation

DRLang's primary API consists of `interpolate()` and `interpolate_dict()` functions. These treat strings as **literal text by default**, only evaluating content that is explicitly marked for interpolation.

### interpolate() Function

The `interpolate()` function processes a template string where:
- Regular text is treated as literal (unchanged)
- `$reference` paths are resolved from context
- `{% expression %}` blocks are evaluated as DRL expressions

**Type Preservation:** If the template contains ONLY a single reference (e.g., `"$value"`), the original type from context is preserved. Mixed content always returns a string.

```python
from drlang import interpolate

context = {"name": "Alice", "count": 5, "price": 19.99}

# Plain strings are unchanged
interpolate("Hello, world!", {})  # "Hello, world!"

# Reference interpolation
interpolate("Hello $name!", context)  # "Hello Alice!"

# Type preservation - single references keep their type
interpolate("$count", context)  # 5 (int)
interpolate("$price", context)  # 19.99 (float)

# Expression blocks (always return strings when mixed with content)
interpolate("Total: {% $count * $price %}", context)  # "Total: 99.95"

# Type-preserving expression blocks - use {%= %} to keep native types
interpolate("{%= 5 + 10 %}", {})  # 15 (int, not "15")
interpolate("{%= $count * 2 %}", context)  # 10 (int, not "10")
interpolate("Result: {%= $count * 2 %}", context)  # "Result: 10" (string, mixed content)

# Mixed content
interpolate("Hi $name, you have {% $count * 2 %} items", context)
# "Hi Alice, you have 10 items"

# Nested references
data = {"user": {"profile": {"name": "Bob"}}}
interpolate("Name: $user>profile>name", data)  # "Name: Bob"

# URL-style templates (bare refs stop at /)
interpolate("https://$domain/api/users/$user_id", 
            {"domain": "api.example.com", "user_id": "123"})
# "https://api.example.com/api/users/123"

# Keys with special characters use bracketed syntax
interpolate("User: $(user name)", {"user name": "Alice"})  # "User: Alice"
interpolate("Value: $(getValue())", {"getValue()": 42})  # "Value: 42"
```

### interpolate_dict() Function

Process multiple templates at once with `interpolate_dict()`:

```python
from drlang import interpolate_dict

templates = {
    "greeting": "Hello $name!",
    "summary": "You have {% $count * 2 %} items",
    "nested": {
        "email": "Contact: $email",
    },
    "items": ["Item: $item1", "Item: $item2"],
}

context = {
    "name": "Alice",
    "count": 5,
    "email": "alice@example.com",
    "item1": "Apple",
    "item2": "Banana",
}

result = interpolate_dict(templates, context)
# {
#     "greeting": "Hello Alice!",
#     "summary": "You have 10 items",
#     "nested": {"email": "Contact: alice@example.com"},
#     "items": ["Item: Apple", "Item: Banana"],
# }
```

## Batch Processing with interpolate_dict

When using `interpolate_dict` to process multiple templates, you can configure it to exclude keys with empty values from the result using the `drop_empty` option. This is useful for cleaning API responses, generating sparse data structures, or handling optional fields.

### Basic Usage

```python
from drlang import interpolate_dict, DRLConfig

templates = {
    "name": "$user>name",
    "email": "$user>email",
    "phone": "$[user>phone]",      # Optional - returns empty string if missing
    "address": "$[user>address]",  # Optional - returns empty string if missing
}

context = {
    "user": {
        "name": "Alice",
        "email": "alice@example.com",
        # phone and address are missing
    }
}

# Default behavior - all keys included (empty strings preserved)
result = interpolate_dict(templates, context)
# Returns: {'name': 'Alice', 'email': 'alice@example.com', 'phone': '', 'address': ''}

# With drop_empty=True - None and empty string values are excluded
config = DRLConfig(drop_empty=True)
result = interpolate_dict(templates, context, config)
# Returns: {'name': 'Alice', 'email': 'alice@example.com'}
```

### Falsy Values Behavior

The `drop_empty` option drops `None` and empty string `""` values. Other falsy values like `0` and `False` are preserved:

```python
templates = {
    "count": 0,            # Falsy but NOT empty - preserved
    "enabled": False,      # Falsy but NOT empty - preserved
    "message": "",         # Empty string - DROPPED
}

config = DRLConfig(drop_empty=True)
result = interpolate_dict(templates, {}, config)
# Returns: {'count': 0, 'enabled': False}
# Only empty strings (and None) are dropped
```

### Real-World Use Case: Email Template Generation

```python
from drlang import interpolate_dict, DRLConfig

# Generate personalized email content
templates = {
    "subject": "Welcome to $company, $user>name!",
    "body": """Dear $user>name,

Thank you for joining $company!

Your account details:
- Email: $user>email
- Plan: {% if($user>premium, 'Premium', 'Free') %}

Best regards,
The $company Team""",
    "footer": "© {% 2026 %} $company. All rights reserved.",
}

context = {
    "company": "Acme Inc",
    "user": {
        "name": "Alice",
        "email": "alice@example.com",
        "premium": True,
    },
}

result = interpolate_dict(templates, context)
print(result["subject"])  # "Welcome to Acme Inc, Alice!"
print(result["body"])     # Personalized email body
```

### Nested Dictionaries

The `interpolate_dict` function works recursively with nested dictionaries:

```python
from drlang import interpolate_dict

templates = {
    "user": {
        "id": "ID: $id",
        "name": "Name: $name",
        "contact": {
            "email": "Email: $email",
            "formatted": "$name <$email>",
        }
    }
}

context = {"id": 123, "name": "Alice", "email": "alice@example.com"}

result = interpolate_dict(templates, context)
# Returns: {
#     'user': {
#         'id': 'ID: 123',
#         'name': 'Name: Alice',
#         'contact': {
#             'email': 'Email: alice@example.com',
#             'formatted': 'Alice <alice@example.com>'
#         }
#     }
# }
```

## Low-Level Expression Evaluation

While `interpolate()` and `interpolate_dict()` are the recommended primary APIs for most use cases, DRLang also exposes the `interpret()` function for direct expression evaluation.

### interpret() Function

The `interpret()` function evaluates a raw DRL expression and returns the result without any string wrapping:

```python
from drlang import interpret

# Direct expression evaluation
interpret("$x + $y", {"x": 10, "y": 5})  # 15

# Function calls
interpret('split($text, ",")', {"text": "a,b,c"})  # ["a", "b", "c"]

# Complex expressions with full type preservation
interpret("$data>values", {"data": {"values": [1, 2, 3]}})  # [1, 2, 3]

# Comparisons and logic
interpret("$age >= 18 and $verified", {"age": 25, "verified": True})  # True

# Conditional logic
interpret("if($score > 50, 'pass', 'fail')", {"score": 75})  # "pass"
```

**When to use `interpret()` instead of `interpolate()`:**
- When you need the raw result of an expression (not a template string)
- For programmatic expression evaluation in rule engines
- When building tools that work with DRL expressions directly
- For the CLI and debugging tools

**When to use `interpolate()` instead:**
- For template strings with literal content mixed with dynamic values
- When generating user-facing text, emails, or configuration files
- For batch processing with `interpolate_dict()`

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

### List Functions
- `list_get(list, index, default=None)` - Safe element access with default value
- `list_slice(list, start, end, step=1)` - Extract subsequence from list
- `list_append(list, item)` - Append item to list (returns new list)
- `list_concat(list1, list2)` - Concatenate two lists
- `list_contains(list, item)` - Check if item exists in list
- `list_index(list, item, default=None)` - Find index of item in list
- `list_reverse(list)` - Reverse list order
- `list_unique(list)` - Remove duplicates while preserving order
- `list_flatten(list)` - Flatten nested list one level

```python
# Safe access with default
drlang.interpret("list_get($items, 10, 'N/A')", {"items": [1, 2, 3]})
# Returns: 'N/A'

# Slice with step
drlang.interpret("list_slice($nums, 0, 10, 2)", {"nums": list(range(10))})
# Returns: [0, 2, 4, 6, 8]

# Check membership
drlang.interpret("list_contains($tags, 'urgent')", {"tags": ["urgent", "important"]})
# Returns: True

# Remove duplicates
drlang.interpret("list_unique($values)", {"values": [1, 2, 2, 3, 1]})
# Returns: [1, 2, 3]
```

### Iteration Functions
- `map(expression, list)` - Transform each element using expression (provides `$item` and `$index`)
- `filter(expression, list)` - Select elements where expression is true (provides `$item` and `$index`)
- `reduce(expression, list, initial=None)` - Accumulate list to single value (provides `$acc`, `$item`, `$index`)

```python
# Double each number
drlang.interpret('map("$item * 2", $nums)', {"nums": [1, 2, 3]})
# Returns: [2, 4, 6]

# Filter even numbers
drlang.interpret('filter("$item % 2 == 0", $nums)', {"nums": [1, 2, 3, 4, 5, 6]})
# Returns: [2, 4, 6]

# Sum all values
drlang.interpret('reduce("$acc + $item", $nums)', {"nums": [1, 2, 3, 4, 5]})
# Returns: 15

# Combine operations
data = {"nums": [1, 2, 3, 4, 5]}
doubled = drlang.interpret('map("$item * 2", $nums)', data)
data["doubled"] = doubled
result = drlang.interpret('filter("$item > 5", $doubled)', data)
# result = [6, 8, 10]
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
