"""
DRLang CLI - Complete Feature Overview
=======================================

The DRLang CLI provides three main capabilities as requested:

1. ABILITY TO TEST INDIVIDUAL LINES/STRINGS
   ✓ Command-line mode: drlang -c 'expression'
   ✓ Interactive mode: Just type expressions directly
   ✓ Supports all DRLang features: math, functions, references, etc.

   Examples:
     $ drlang -c "2 + 3 * 4"
     14
     
     $ drlang -c 'upper("hello")'
     HELLO
     
     $ drlang
     drlang> $user>name
     => 'Alice'

2. ABILITY TO ITERATIVELY TEST DICTIONARIES OF KEY/EXPRESSION PAIRS
   ✓ test command: Evaluate multiple expressions at once
   ✓ File support: Load expressions from JSON
   ✓ Batch testing: See all results in a formatted table
   ✓ Programmatic API: interpolate_dict() function

   Examples:
     drlang> test {"name": "$user>name", "adult": "$user>age >= 18"}
     
     drlang> test file expressions.json
     
     Python:
       results = interpolate_dict(templates, context)

3. HELP FUNCTION FOR AVAILABLE FUNCTIONS
   ✓ functions command: List all 40+ built-in functions
   ✓ Category filtering: Filter by pattern (e.g., "functions regex")
   ✓ Detailed help: Get documentation for specific functions
   ✓ Signature display: See function parameters and types
   ✓ Examples: Built-in usage examples

   Examples:
     drlang> functions
     (Lists all functions by category)
     
     drlang> functions str
     (Shows only string functions)
     
     drlang> help split
     (Shows detailed help for split function)

ADDITIONAL FEATURES
===================

Context Management:
  - set <key> <json>          Add data to context
  - unset <key>               Remove data
  - context                   View all context data
  - context load <file>       Load from JSON file
  - context clear             Clear all data

Configuration:
  - config                    View current syntax
  - config set <ref> <delim>  Set custom syntax
  - config reset              Reset to defaults

Utilities:
  - last                      Show last result
  - examples                  Show usage patterns
  - exit/quit                 Exit shell

Command-Line Arguments:
  -c COMMAND                  Evaluate expression and exit
  -f FILE                     Load context from file
  -e EXPR                     Expression (requires -f)
  --ref REF                   Custom reference indicator
  --delim DELIM               Custom key delimiter

USAGE PATTERNS
==============

Quick Testing:
  $ drlang -c 'expression'

With Data:
  $ drlang -f data.json -c '$user>name'

Interactive Session:
  $ drlang
  drlang> set user {"name": "Alice", "age": 30}
  drlang> $user>name
  => 'Alice'
  drlang> functions
  drlang> help upper
  drlang> exit

Batch Testing:
  $ drlang -f data.json
  drlang> test file expressions.json

Custom Syntax:
  $ drlang --ref @ --delim .
  drlang> @user.name

TESTING
=======

All features have been tested and verified:
  ✓ Expression evaluation (single & batch)
  ✓ Context management (set, load, clear)
  ✓ Function discovery and help
  ✓ Custom syntax configuration
  ✓ File I/O (JSON loading)
  ✓ Error handling and reporting
  ✓ Command-line and interactive modes

Run test_cli.py to verify all functionality.
"""

if __name__ == "__main__":
    print(__doc__)
