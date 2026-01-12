# DRL (Dynamic Reference Language) - AI Coding Agent Guide

## Project Overview
DRL is a fully-implemented configuration management library that interprets string-based expressions to extract and process data from dict-like sources. It features a customizable syntax, mathematical operators, 40+ built-in functions, and comprehensive test coverage.

## Architecture (Fully Implemented)

### Core Components
- **[src/drl/language.py](../src/drl/language.py)** (442 lines) - Complete DRL parser/interpreter
  - `DRLConfig` class for custom syntax configuration
  - `tokenize()` - Lexical analysis with configurable symbols
  - `parse_line()` - Expression parser with operator precedence
  - `evaluate()` - AST evaluator with reference resolution
  - `interpret()` - Main public API
  
- **[src/drl/functions.py](../src/drl/functions.py)** (153 lines) - Function registry
  - `FUNCTIONS` dict with 40+ built-in functions
  - `convert_arg_types()` - Automatic type conversion using inspect
  - `execute()` - Function dispatcher with type conversion
  
- **[src/drl/__init__.py](../src/drl/__init__.py)** - Public API exports
  - Exports: `interpret()`, `DRLConfig`

### Test Suite (112 tests, all passing)
- **[tests/test_language.py](../tests/test_language.py)** - 42 tests for parser/interpreter
- **[tests/test_functions.py](../tests/test_functions.py)** - 11 tests for function execution
- **[tests/test_operators.py](../tests/test_operators.py)** - 33 tests for mathematical operators
- **[tests/test_custom_syntax.py](../tests/test_custom_syntax.py)** - 31 tests for DRLConfig

## Key Features

### 1. Customizable Syntax (NEW!)
DRL now supports custom reference indicators and key delimiters via `DRLConfig`:

```python
from drl import interpret, DRLConfig

# Default syntax: $ and >
interpret('$root>timestamp', {'root': {'timestamp': 1234}})  # 1234

# JavaScript-style: @ and .
config = DRLConfig('@', '.')
interpret('@user.name', {'user': {'name': 'Alice'}}, config)  # "Alice"

# Path-style: # and /
config = DRLConfig('#', '/')
interpret('#root/path/value', {'root': {'path': {'value': 42}}}, config)  # 42

# C++-style: & and ::
config = DRLConfig('&', '::')
interpret('&ns::cls::method', {'ns': {'cls': {'method': 'ok'}}}, config)  # "ok"
```

**Restrictions:**
- Reference indicators cannot be: `(`, `)`, `,`, `'`, `"`, whitespace
- Key delimiters cannot be: `(`, `)`, `,`, `'`, `"`, whitespace
- Operators (`+`, `-`, `*`, `/`, `%`, `^`) can be used as delimiters but may cause ambiguity

### 2. Mathematical Operators
Supports: `+`, `-`, `*`, `/`, `%`, `^` with proper precedence:

```python
interpret('2 + 3 * 4', {})  # 14 (not 20)
interpret('(2 + 3) * 4', {})  # 20
interpret('2 ^ 3', {})  # 8 (exponentiation)
interpret('$x * 2 + $y', {'x': 5, 'y': 10})  # 20
```

**Precedence (high to low):** `^` > `*`, `/`, `%` > `+`, `-`

### 3. Function System
40+ built-in functions with automatic type conversion:

**Categories:**
- **String:** split, upper, lower, replace, strip, lstrip, rstrip
- **Math:** max, min, abs, round, floor, ceil, sqrt, pow
- **Type:** int, float, str, bool
- **Collection:** len, join, sorted, reversed, sum
- **Random:** random, randint, choice
- **DateTime:** now, today, strftime
- **I/O:** print

**Example:**
```python
interpret('split($data, ",")', {'data': 'a,b,c'})  # ['a', 'b', 'c']
interpret('max($x, $y)', {'x': 10, 'y': 20})  # 20
interpret('len($name) * 2', {'name': 'Alice'})  # 10
```

### 4. Reference Resolution
Navigate nested dictionaries with space-aware key handling:

```python
# Standard nested access
interpret('$root>user>name', {'root': {'user': {'name': 'Bob'}}})  # "Bob"

# Keys with spaces
interpret('$user info>full name', {'user info': {'full name': 'Bob'}})  # "Bob"

# With custom syntax
config = DRLConfig('@', '.')
interpret('@data.nested.value', {'data': {'nested': {'value': 99}}}, config)  # 99
```

## Development Patterns

### Parser Design
The interpreter follows a three-stage pipeline:
1. **Tokenize:** `tokenize(expression, config)` → List[Token]
   - Recognizes: references, operators, functions, literals, parentheses
   - Config-aware: uses `config.ref_indicator` and `config.key_delimiter`
   
2. **Parse:** `parse_line(line, config)` → Token or nested structure
   - Handles operator precedence and parentheses
   - Returns single Token for simple expressions or nested list for complex ones
   
3. **Evaluate:** `evaluate(parsed, context, config)` → Any
   - Resolves references via `resolve_reference()`
   - Executes functions via `functions.execute()`
   - Applies operators recursively

### Type Conversion
Functions automatically convert arguments based on type hints:

```python
# In FUNCTIONS dict
'max': max  # Uses max's signature: max(*args) with type hints

# convert_arg_types() inspects signature and converts:
execute('max', '10', '20')  # Converts strings → ints → returns 20
```

### Testing Strategy
- **Language tests:** Tokenization, parsing, evaluation, edge cases
- **Function tests:** Execution via `execute()`, type conversion
- **Operator tests:** Precedence, parentheses, with references/functions
- **Custom syntax tests:** All features with different DRLConfig settings

## Key Implementation Details

### DRLConfig Class
```python
class DRLConfig:
    def __init__(self, ref_indicator: str = "$", key_delimiter: str = ">"):
        # Validates symbols don't conflict with reserved syntax
        self.ref_indicator = ref_indicator
        self.key_delimiter = key_delimiter
```

### Tokenizer Behavior
- Stops at operators when collecting references (prevents `$a+b` from being one token)
- Excludes `config.key_delimiter` from stop_chars during reference collection
- Handles multi-character delimiters (e.g., `::`)

### Reference Resolution
```python
def resolve_reference(ref_path: str, context: Dict, config: DRLConfig) -> Any:
    keys = ref_path.split(config.key_delimiter)
    # Navigate through nested dicts
    # Raises NameError if key missing
    # Raises TypeError if trying to navigate non-dict
```

## Critical Implementation Notes

1. **Operator Precedence:** Implemented via recursive parsing with precedence levels
2. **Type Safety:** Functions.execute() converts args to match function signatures
3. **Error Handling:** 
   - NameError for missing references/functions
   - TypeError for invalid operations
4. **Custom Syntax Edge Cases:**
   - Using operators as delimiters works but can create ambiguity
   - Test extensively when delimiter is an operator (e.g., `/`)
5. **Space Handling:** Keys can contain spaces; tokenizer handles this correctly

## Common Development Tasks

### Adding a New Function
1. Add to `FUNCTIONS` dict in [functions.py](../src/drl/functions.py)
2. Use type hints for automatic conversion
3. Add test in [tests/test_functions.py](../tests/test_functions.py)

### Modifying Parser
- Tokenizer changes affect [tokenize()](../src/drl/language.py)
- Operator precedence in [parse_line()](../src/drl/language.py)
- Evaluation logic in [evaluate()](../src/drl/language.py)
- Always run full test suite: `python -m pytest tests/`

### Custom Syntax Testing
- Test with multiple config combinations
- Verify operators, functions, and nested references work
- Check edge cases with operator-based delimiters
- See [tests/test_custom_syntax.py](../tests/test_custom_syntax.py) for patterns
