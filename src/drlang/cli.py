"""DRLang Command-Line Interface.

Provides an interactive shell for testing DRLang expressions, managing context data,
and exploring available functions.
"""

import cmd
import json
import sys
from typing import Dict, Any, Optional
import inspect

from drlang import interpret, interpret_dict, DRLConfig
from drlang.functions import FUNCTIONS
from drlang import (
    DRLError,
)


class DRLangShell(cmd.Cmd):
    """Interactive shell for testing DRLang expressions."""

    intro = """
╔════════════════════════════════════════════════════════════════════╗
║                   DRLang Interactive Shell                         ║
║                                                                    ║
║  Test expressions, explore functions, and debug your DRLang code  ║
║  Type 'help' or '?' for available commands                        ║
╚════════════════════════════════════════════════════════════════════╝
"""
    prompt = "drlang> "

    def __init__(self):
        super().__init__()
        self.context: Dict[str, Any] = {}
        self.config: Optional[DRLConfig] = None
        self.last_result = None

    def emptyline(self):
        """Do nothing on empty line."""
        return False

    def default(self, line):
        """Evaluate DRLang expression by default."""
        if line.strip():
            self.do_eval(line)

    def do_eval(self, line):
        """Evaluate a DRLang expression.

        Usage: eval <expression>
        Or simply: <expression>

        Examples:
            eval $user>name
            $user>age * 2
            if($user>age >= 18, "adult", "minor")
        """
        if not line.strip():
            print("Error: Expression required")
            return

        try:
            result = interpret(line.strip(), self.context, self.config)
            self.last_result = result
            print(f"=> {result!r}")
        except DRLError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def do_set(self, line):
        """Set a context variable.

        Usage: set <key> <json_value>

        Examples:
            set user {"name": "Alice", "age": 30}
            set count 42
            set active true
            set tags ["python", "drlang"]
        """
        parts = line.split(None, 1)
        if len(parts) < 2:
            print("Error: Usage: set <key> <json_value>")
            return

        key, value_str = parts
        try:
            value = json.loads(value_str)
            self.context[key] = value
            print(f"Set {key} = {value!r}")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON - {e}")

    def do_unset(self, key):
        """Remove a context variable.

        Usage: unset <key>
        """
        if not key:
            print("Error: Key required")
            return

        if key in self.context:
            del self.context[key]
            print(f"Removed {key}")
        else:
            print(f"Error: Key '{key}' not found")

    def do_context(self, line):
        """Show or load context data.

        Usage:
            context                    - Show current context
            context load <file.json>   - Load context from JSON file
            context clear              - Clear all context data
        """
        if not line.strip():
            if self.context:
                print("Current context:")
                print(json.dumps(self.context, indent=2))
            else:
                print("Context is empty")
            return

        parts = line.split(None, 1)
        command = parts[0].lower()

        if command == "clear":
            self.context.clear()
            print("Context cleared")
        elif command == "load" and len(parts) == 2:
            filename = parts[1]
            try:
                with open(filename, "r") as f:
                    self.context = json.load(f)
                print(f"Loaded context from {filename}")
                print(f"Keys: {list(self.context.keys())}")
            except FileNotFoundError:
                print(f"Error: File '{filename}' not found")
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in file - {e}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Error: Usage: context [load <file> | clear]")

    def do_test(self, line):
        """Test multiple expressions from a dictionary mapping.

        Usage:
            test <json_dict>           - Test expressions from inline JSON
            test file <file.json>      - Test expressions from JSON file

        The JSON should be a dictionary where keys are labels and values are
        DRLang expressions to evaluate.

        Examples:
            test {"name": "$user>name", "adult": "$user>age >= 18"}
            test file expressions.json
        """
        if not line.strip():
            print("Error: Usage: test <json_dict> OR test file <file.json>")
            return

        parts = line.split(None, 1)

        if parts[0].lower() == "file" and len(parts) == 2:
            filename = parts[1]
            try:
                with open(filename, "r") as f:
                    expressions = json.load(f)
            except FileNotFoundError:
                print(f"Error: File '{filename}' not found")
                return
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in file - {e}")
                return
        else:
            try:
                expressions = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON - {e}")
                return

        if not isinstance(expressions, dict):
            print("Error: Input must be a dictionary")
            return

        print("\nTesting expressions:")
        print("=" * 70)

        try:
            results = interpret_dict(expressions, self.context, self.config)
            for key, value in results.items():
                expr = (
                    expressions[key]
                    if isinstance(expressions[key], str)
                    else "<nested>"
                )
                print(f"{key:20} {expr:30} => {value!r}")
        except DRLError as e:
            print(f"Error during evaluation: {e}")

        print("=" * 70)

    def do_functions(self, pattern=""):
        """List all available functions or search by pattern.

        Usage:
            functions              - List all functions
            functions <pattern>    - Filter by pattern (case-insensitive)

        Examples:
            functions
            functions str
            functions regex
        """
        pattern = pattern.lower().strip()
        matching = []

        for name in sorted(FUNCTIONS.keys()):
            if not pattern or pattern in name.lower():
                matching.append(name)

        if not matching:
            print(f"No functions matching '{pattern}'")
            return

        print(f"\nAvailable functions ({len(matching)}):")
        print("=" * 70)

        # Group by category
        categories = {
            "String": [
                "split",
                "upper",
                "lower",
                "capitalize",
                "strip",
                "replace",
                "find",
                "join",
            ],
            "Math": ["max", "min", "int", "float", "abs", "round"],
            "Type": ["str", "bool", "int", "float"],
            "Collection": ["len", "sorted", "reversed", "sum", "all", "any"],
            "Conditional": ["if"],
            "Random": [
                "random",
                "randint",
                "uniform",
                "randrange",
                "choice",
                "shuffle",
            ],
            "DateTime": [
                "datetime",
                "date",
                "time",
                "timedelta",
                "strptime",
                "strftime",
            ],
            "Regex": [
                "regex_search",
                "regex_match",
                "regex_findall",
                "regex_sub",
                "regex_split",
                "regex_extract",
            ],
            "I/O": ["print"],
        }

        categorized = set()
        for category, funcs in categories.items():
            category_matches = [f for f in funcs if f in matching]
            if category_matches:
                print(f"\n{category}:")
                for func in category_matches:
                    print(f"  • {func}")
                    categorized.update(category_matches)

        # Show uncategorized functions
        uncategorized = [f for f in matching if f not in categorized]
        if uncategorized:
            print("\nOther:")
            for func in uncategorized:
                print(f"  • {func}")

        print("\nType 'help <function_name>' for detailed help on a specific function.")

    def do_help(self, arg):
        """Show help for commands or functions.

        Usage:
            help                  - Show all commands
            help <command>        - Show help for a specific command
            help <function_name>  - Show help for a DRLang function

        Examples:
            help eval
            help split
            help if
        """
        if not arg:
            # Show all commands
            super().do_help(arg)
            return

        # Check if it's a DRLang function
        if arg in FUNCTIONS:
            self._show_function_help(arg)
        else:
            # Check if it's a command
            super().do_help(arg)

    def _show_function_help(self, func_name):
        """Show detailed help for a specific function."""
        func = FUNCTIONS[func_name]

        print(f"\nFunction: {func_name}")
        print("=" * 70)

        # Get function signature
        try:
            sig = inspect.signature(func)
            print(f"Signature: {func_name}{sig}")
        except (ValueError, TypeError):
            print(f"Signature: {func_name}(...)")

        # Get docstring
        doc = inspect.getdoc(func)
        if doc:
            print(f"\n{doc}")
        else:
            print("\nNo documentation available.")

        print("\nUsage in DRLang:")
        print(f"  {func_name}(arg1, arg2, ...)")
        print(f"  Example: {func_name}($data, 'value')")

    def do_config(self, line):
        """Configure DRLang syntax.

        Usage:
            config                            - Show current config
            config set <ref> <delim>          - Set custom syntax
            config reset                      - Reset to default syntax

        Examples:
            config set @ .
            config set # /
            config reset
        """
        if not line.strip():
            if self.config:
                print("Custom config:")
                print(f"  Reference indicator: {self.config.ref_indicator}")
                print(f"  Key delimiter: {self.config.key_delimiter}")
            else:
                print("Using default config ($ and >)")
            return

        parts = line.split()
        if parts[0].lower() == "reset":
            self.config = None
            print("Reset to default config ($ and >)")
        elif parts[0].lower() == "set" and len(parts) == 3:
            ref_indicator, key_delimiter = parts[1], parts[2]
            try:
                self.config = DRLConfig(ref_indicator, key_delimiter)
                print(f"Set custom config: {ref_indicator} and {key_delimiter}")
            except ValueError as e:
                print(f"Error: {e}")
        else:
            print("Error: Usage: config [set <ref> <delim> | reset]")

    def do_last(self, line):
        """Show the last evaluation result."""
        if self.last_result is not None:
            print(f"Last result: {self.last_result!r}")
        else:
            print("No previous result")

    def do_examples(self, line):
        """Show example expressions and usage patterns."""
        examples = """
DRLang Examples
═══════════════════════════════════════════════════════════════════════

Data References:
    $user>name                     - Access nested data
    $[user>age]                    - Optional reference (returns None)
    $(user>email)                  - Required reference (throws error)
    ${user>title}                  - Literal fallback (returns string)

Math Operations:
    $price * 0.15                  - Arithmetic operations
    ($a + $b) * 2                  - Operator precedence
    2 ^ 3                          - Exponentiation (8)

Comparisons:
    $age >= 18                     - Greater than or equal
    $status == "active"            - Equality
    $count != 0                    - Not equal

Logic:
    $active and $verified          - Logical AND
    $premium or $trial             - Logical OR
    not $disabled                  - Logical NOT

String Functions:
    upper($name)                   - Convert to uppercase
    split($tags, ",")              - Split string
    replace($text, "old", "new")   - Replace text
    len($message)                  - String length

Conditionals:
    if($age >= 18, "adult", "minor")
    if($[premium], $rate * 0.9, $rate)

Math Functions:
    max($x, $y)                    - Maximum value
    min(10, $count)                - Minimum value
    int($price)                    - Convert to integer

═══════════════════════════════════════════════════════════════════════
"""
        print(examples)

    def do_exit(self, line):
        """Exit the shell."""
        print("Goodbye!")
        return True

    def do_quit(self, line):
        """Exit the shell."""
        return self.do_exit(line)

    def do_EOF(self, line):
        """Exit on Ctrl+D (Unix) or Ctrl+Z (Windows)."""
        print()
        return self.do_exit(line)


def main():
    """Main entry point for the CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="DRLang Interactive Shell - Test and debug DRLang expressions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
Examples:
  drlang                           - Start interactive shell
  drlang -c "$user>name"           - Evaluate single expression
  drlang -f data.json -e "\$user>age * 2"
        """,
    )
    parser.add_argument("-c", "--command", help="Evaluate a single expression and exit")
    parser.add_argument("-f", "--file", help="Load context data from JSON file")
    parser.add_argument("-e", "--expr", help="Expression to evaluate (requires -f)")
    parser.add_argument(
        "--ref", default="$", help="Custom reference indicator (default: $)"
    )
    parser.add_argument(
        "--delim", default=">", help="Custom key delimiter (default: >)"
    )

    args = parser.parse_args()

    # Single command mode
    if args.command:
        context = {}
        if args.file:
            try:
                with open(args.file, "r") as f:
                    context = json.load(f)
            except Exception as e:
                print(f"Error loading context: {e}", file=sys.stderr)
                sys.exit(1)

        config = None
        if args.ref != "$" or args.delim != ">":
            config = DRLConfig(args.ref, args.delim)

        try:
            result = interpret(args.command, context, config)
            print(result)
        except DRLError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Expression with file mode
    if args.expr:
        if not args.file:
            print("Error: -e/--expr requires -f/--file", file=sys.stderr)
            sys.exit(1)

        try:
            with open(args.file, "r") as f:
                context = json.load(f)
        except Exception as e:
            print(f"Error loading context: {e}", file=sys.stderr)
            sys.exit(1)

        config = None
        if args.ref != "$" or args.delim != ">":
            config = DRLConfig(args.ref, args.delim)

        try:
            result = interpret(args.expr, context, config)
            print(result)
        except DRLError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # Interactive mode
    shell = DRLangShell()

    # Load context if provided
    if args.file:
        try:
            with open(args.file, "r") as f:
                shell.context = json.load(f)
            print(f"Loaded context from {args.file}")
            print(f"Keys: {list(shell.context.keys())}")
        except Exception as e:
            print(f"Warning: Could not load context: {e}")

    # Set custom config if provided
    if args.ref != "$" or args.delim != ">":
        try:
            shell.config = DRLConfig(args.ref, args.delim)
            print(f"Using custom syntax: {args.ref} and {args.delim}")
        except ValueError as e:
            print(f"Warning: Invalid config: {e}")

    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
