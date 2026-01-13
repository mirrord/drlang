"""Demo script showing DRLang CLI capabilities."""

print(
    """
╔════════════════════════════════════════════════════════════════════╗
║                   DRLang CLI Demo                                  ║
╚════════════════════════════════════════════════════════════════════╝

The DRLang CLI provides an interactive environment for testing and
debugging DRLang expressions.

1. INTERACTIVE SHELL
   Launch with: drlang
   
   Try these commands:
     set user {"name": "Alice", "age": 30}
     $user>name
     $user>age * 2
     if($user>age >= 18, "adult", "minor")
     functions
     help split
     examples

2. COMMAND-LINE EVALUATION
   Single expression:
     drlang -c '$user>name' -f data.json
   
   Output: Alice

3. BATCH TESTING
   Create expressions.json:
     {
       "name": "$user>name",
       "adult": "$user>age >= 18",
       "greeting": "upper($user>name)"
     }
   
   In shell:
     context load data.json
     test file expressions.json

4. CUSTOM SYNTAX
   Use different reference symbols:
     drlang --ref @ --delim .
   
   Then: @user.name instead of $user>name

5. FUNCTION DOCUMENTATION
   Interactive help:
     drlang
     > functions           # List all
     > functions str       # Filter by pattern
     > help split          # Detailed help
     > help regex_extract  # Regex function help

6. CONTEXT MANAGEMENT
   In shell:
     set users [{"name": "Alice"}, {"name": "Bob"}]
     $users>0>name
     context               # View all data
     context clear         # Reset
     context load data.json  # Load from file

═══════════════════════════════════════════════════════════════════════

Try it now:
  python -m drlang.cli

Or with data:
  python -m drlang.cli -f test_data.json

For quick tests:
  python -m drlang.cli -c 'upper("hello")'
  python -m drlang.cli -f test_data.json -c '$user>name'

═══════════════════════════════════════════════════════════════════════
"""
)
