# this module contains the logic for the DRL language.
from typing import Any, Dict, List, Union, Optional, Callable
import drl.functions as functions


class DRLConfig:
    """Configuration for DRL syntax symbols."""

    def __init__(
        self,
        ref_indicator: str = "$",
        key_delimiter: str = ">",
        custom_functions: Optional[Dict[str, Callable]] = None,
    ):
        """Initialize DRL configuration.

        Args:
            ref_indicator: Symbol to indicate data references (default: '$')
            key_delimiter: Symbol to separate nested keys (default: '>')
            custom_functions: Optional dict of custom functions to register {name: Callable}
        """
        # Validate that reference indicator doesn't conflict with critical syntax
        # Key delimiters are only used within references so they're more flexible
        ref_reserved = "(),'\" \t\n\r"
        if ref_indicator in ref_reserved:
            raise ValueError(
                f"Reference indicator '{ref_indicator}' conflicts with reserved syntax"
            )

        # Disallow multi-character operators as key delimiters to avoid ambiguity
        key_reserved = "(),'\" \t\n\r"
        if key_delimiter in key_reserved:
            raise ValueError(
                f"Key delimiter '{key_delimiter}' conflicts with reserved syntax"
            )

        self.ref_indicator = ref_indicator
        self.key_delimiter = key_delimiter
        self.custom_functions = custom_functions or {}


# Default configuration
DEFAULT_CONFIG = DRLConfig()


class Token:
    """Represents a token in a DRL expression."""

    def __init__(self, type_: str, value: str):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


def tokenize(expression: str, config: Optional[DRLConfig] = None) -> List[Token]:
    """Tokenize a DRL expression into tokens.

    Handles:
    - Data references: {ref_indicator}key{key_delimiter}nested{key_delimiter}path
    - Function names: identifier followed by (
    - String literals: 'value' or "value"
    - Numeric literals: 123, 45.67
    - Operators: +, -, *, /, %, ^
    - Delimiters: ( ) ,

    Args:
        expression: The DRL expression to tokenize
        config: Optional DRLConfig with custom syntax symbols
    """
    if config is None:
        config = DEFAULT_CONFIG

    tokens = []
    i = 0

    while i < len(expression):
        # Skip whitespace
        if expression[i].isspace():
            i += 1
            continue

        # Data reference: {ref_indicator}key{key_delimiter}nested{key_delimiter}path
        if expression[i] == config.ref_indicator:
            i += 1
            ref = ""
            # Collect reference path (can include spaces in keys)
            # Stop at operators, comparison operators, delimiters, and quotes
            base_stop_chars = "(),'\"+-*/%^<>=!"
            # Remove key_delimiter from stop_chars if it's in there
            stop_chars = "".join(
                c for c in base_stop_chars if c != config.key_delimiter
            )
            stop_chars += config.ref_indicator

            while i < len(expression):
                # Special handling for key_delimiter when it might also be a comparison operator
                if (
                    expression[i] == config.key_delimiter
                    and config.key_delimiter in "<>="
                ):
                    # Check if this is a comparison operator or a key delimiter
                    # It's a comparison operator if:
                    # 1. Followed by space, end of string, or another operator char (like = for >=)
                    # 2. Not followed by a valid identifier character
                    next_pos = i + 1
                    if next_pos >= len(expression):
                        # End of expression, this is a comparison operator
                        break
                    next_char = expression[next_pos]
                    if next_char.isspace() or next_char in "=!<>(),'\"+-*/%^":
                        # This is a comparison operator, not a key delimiter
                        break
                    # Otherwise, it's a key delimiter, continue collecting the reference

                # Stop at stop characters
                if expression[i] in stop_chars:
                    break

                # If we hit a space, peek ahead to see what comes next
                if expression[i].isspace():
                    # Look ahead past whitespace
                    j = i + 1
                    while j < len(expression) and expression[j].isspace():
                        j += 1

                    if j < len(expression):
                        # Stop if next non-space char is a stop character
                        if expression[j] in stop_chars:
                            # Don't include this space
                            break

                        # Check for comparison operators that might have been removed from stop_chars
                        if (
                            config.key_delimiter in "<>="
                            and expression[j] == config.key_delimiter
                        ):
                            # Peek ahead to see if it's a comparison operator
                            next_pos = j + 1
                            if next_pos >= len(expression):
                                break
                            next_char = expression[next_pos]
                            if next_char.isspace() or next_char in "=!<>(),'\"+-*/%^":
                                break

                        # Stop if next word is a logical keyword
                        if j + 3 <= len(expression) and expression[j : j + 3] in [
                            "and",
                            "not",
                        ]:
                            if (
                                j + 3 == len(expression)
                                or not expression[j + 3].isalnum()
                            ):
                                break
                        if j + 2 <= len(expression) and expression[j : j + 2] == "or":
                            if (
                                j + 2 == len(expression)
                                or not expression[j + 2].isalnum()
                            ):
                                break

                ref += expression[i]
                i += 1
            tokens.append(Token("REFERENCE", ref.strip()))
            continue

        # String literal
        if expression[i] in "\"'":
            quote = expression[i]
            i += 1
            string = ""
            while i < len(expression) and expression[i] != quote:
                if expression[i] == "\\" and i + 1 < len(expression):
                    # Handle escape sequences
                    i += 1
                    string += expression[i]
                else:
                    string += expression[i]
                i += 1
            if i < len(expression):
                i += 1  # Skip closing quote
            tokens.append(Token("STRING", string))
            continue

        # Delimiters
        if expression[i] == "(":
            tokens.append(Token("LPAREN", "("))
            i += 1
            continue

        if expression[i] == ")":
            tokens.append(Token("RPAREN", ")"))
            i += 1
            continue

        if expression[i] == ",":
            tokens.append(Token("COMMA", ","))
            i += 1
            continue

        # Mathematical operators
        if expression[i] in "+-*/":
            tokens.append(Token("OPERATOR", expression[i]))
            i += 1
            continue

        # Power operator
        if expression[i] == "^":
            tokens.append(Token("OPERATOR", "^"))
            i += 1
            continue

        # Modulo operator
        if expression[i] == "%":
            tokens.append(Token("OPERATOR", "%"))
            i += 1
            continue

        # Comparison operators (two-character: ==, !=, <=, >=)
        if i + 1 < len(expression):
            two_char = expression[i : i + 2]
            if two_char in ["==", "!=", "<=", ">="]:
                tokens.append(Token("COMPARISON", two_char))
                i += 2
                continue

        # Single-character comparison operators (< and >)
        if expression[i] in "<>":
            tokens.append(Token("COMPARISON", expression[i]))
            i += 1
            continue

        # Exclamation mark for 'not' (handled as part of !=, but standalone is invalid)
        if expression[i] == "!":
            # If we reach here, it's not part of !=, so it's invalid
            raise SyntaxError(f"Unexpected '!' at position {i}")

        # Numeric literals
        if expression[i].isdigit() or (
            expression[i] == "."
            and i + 1 < len(expression)
            and expression[i + 1].isdigit()
        ):
            num = ""
            has_dot = False
            while i < len(expression) and (
                expression[i].isdigit() or (expression[i] == "." and not has_dot)
            ):
                if expression[i] == ".":
                    has_dot = True
                num += expression[i]
                i += 1
            tokens.append(Token("NUMBER", num))
            continue

        # Function name or bare identifier
        if expression[i].isalpha() or expression[i] == "_":
            name = ""
            while i < len(expression) and (
                expression[i].isalnum() or expression[i] == "_"
            ):
                name += expression[i]
                i += 1

            # Check for boolean literals
            if name == "True":
                tokens.append(Token("BOOLEAN", "True"))
                continue
            elif name == "False":
                tokens.append(Token("BOOLEAN", "False"))
                continue
            # Check for logical operators
            elif name in ["and", "or"]:
                tokens.append(Token("LOGICAL", name))
                continue
            elif name == "not":
                tokens.append(Token("NOT", "not"))
                continue

            # Look ahead to see if this is a function call
            j = i
            while j < len(expression) and expression[j].isspace():
                j += 1
            if j < len(expression) and expression[j] == "(":
                tokens.append(Token("FUNCTION", name))
            else:
                tokens.append(Token("IDENTIFIER", name))
            continue

        # Unknown character - skip it
        i += 1

    return tokens


def resolve_reference(
    reference: str, context: Dict[str, Any], config: Optional[DRLConfig] = None
) -> Any:
    """Resolve a data reference like 'root>timestamp' from context dict.

    Args:
        reference: The reference path (e.g., 'root>timestamp')
        context: The data dictionary to resolve from
        config: Optional DRLConfig with custom key delimiter

    Returns:
        The resolved value

    Raises:
        KeyError: If the reference path doesn't exist
    """
    if config is None:
        config = DEFAULT_CONFIG

    parts = reference.split(config.key_delimiter)
    value = context

    for part in parts:
        part = part.strip()
        if isinstance(value, dict):
            value = value[part]
        else:
            raise TypeError(f"Cannot navigate into non-dict value at '{part}'")

    return value


def parse_line(
    line: str, config: Optional[DRLConfig] = None
) -> Union[Token, List, None]:
    """Parse a DRL expression into a structure suitable for evaluation.

    Args:
        line: The DRL expression to parse
        config: Optional DRLConfig with custom syntax symbols

    Returns a list representation where:
    - Simple tokens are returned as-is
    - Function calls are returned as nested lists: [function_name, arg1, arg2, ...]
    - Operator expressions: ['OPERATOR', operator, left, right]
    """
    if config is None:
        config = DEFAULT_CONFIG

    tokens = tokenize(line, config)

    if not tokens:
        return None

    # Simple case: just a reference, number, or boolean
    if len(tokens) == 1:
        if tokens[0].type in ("REFERENCE", "NUMBER", "BOOLEAN"):
            return tokens[0]

    # Operator precedence (lower number = higher precedence)
    precedence = {
        "^": 1,  # Power
        "*": 2,
        "/": 2,
        "%": 2,  # Modulo
        "+": 3,
        "-": 3,
        "<": 4,  # Comparison operators
        ">": 4,
        "<=": 4,
        ">=": 4,
        "==": 5,
        "!=": 5,
        "not": 6,  # Logical not (unary)
        "and": 7,  # Logical and
        "or": 8,  # Logical or
    }

    def parse_expression_with_precedence(tokens, start=0, min_precedence=999):
        """Parse expression with operator precedence."""
        # Handle unary 'not'
        if start < len(tokens) and tokens[start].type == "NOT":
            start += 1
            operand, start = parse_expression_with_precedence(
                tokens, start, precedence.get("not", 6) + 1
            )
            left = ["NOT", operand]
        else:
            left, start = parse_primary(tokens, start)

        while start < len(tokens):
            # Check if next token is an operator, comparison, or logical
            token_type = tokens[start].type
            if token_type in ["OPERATOR", "COMPARISON", "LOGICAL"]:
                op = tokens[start].value
                op_precedence = precedence.get(op, 999)

                if op_precedence >= min_precedence:
                    break

                start += 1  # Consume operator

                # Parse right side with higher precedence
                right, start = parse_expression_with_precedence(
                    tokens, start, op_precedence + 1
                )

                # Create operator node
                if token_type == "COMPARISON":
                    left = ["COMPARISON", op, left, right]
                elif token_type == "LOGICAL":
                    left = ["LOGICAL", op, left, right]
                else:
                    left = ["OPERATOR", op, left, right]
            else:
                break

        return left, start

    def parse_primary(tokens, start=0):
        """Parse a primary expression (function call, value, or parenthesized expression)."""
        if start >= len(tokens):
            return None, start

        token = tokens[start]

        # Parenthesized expression
        if token.type == "LPAREN":
            start += 1
            expr, start = parse_expression_with_precedence(tokens, start)
            if start < len(tokens) and tokens[start].type == "RPAREN":
                start += 1
            return expr, start

        # Function call
        if token.type == "FUNCTION":
            func_name = token.value
            start += 1

            # Expect LPAREN
            if start >= len(tokens) or tokens[start].type != "LPAREN":
                raise SyntaxError(f"Expected '(' after function name '{func_name}'")
            start += 1

            # Parse arguments
            args = []
            while start < len(tokens) and tokens[start].type != "RPAREN":
                # Skip commas
                if tokens[start].type == "COMMA":
                    start += 1
                    continue

                # Parse argument (could be reference, string, nested function, or expression)
                arg, start = parse_expression_with_precedence(tokens, start)
                if arg is not None:
                    args.append(arg)

            # Expect RPAREN
            if start >= len(tokens) or tokens[start].type != "RPAREN":
                raise SyntaxError("Expected ')' after function arguments")
            start += 1

            return [func_name] + args, start

        # Simple value (reference, string, number, or identifier)
        return token, start + 1

    result, _ = parse_expression_with_precedence(tokens)
    return result


def evaluate(
    parsed, context: Dict[str, Any], config: Optional[DRLConfig] = None
) -> Any:
    """Evaluate a parsed DRL expression.

    Args:
        parsed: Result from parse_line()
        context: The data dictionary
        config: Optional DRLConfig with custom syntax symbols

    Returns:
        The evaluated result
    """
    if config is None:
        config = DEFAULT_CONFIG

    # Handle Token directly
    if isinstance(parsed, Token):
        if parsed.type == "REFERENCE":
            return resolve_reference(parsed.value, context, config)
        elif parsed.type == "STRING":
            return parsed.value
        elif parsed.type == "NUMBER":
            # Parse as float if it has a decimal point, otherwise int
            if "." in parsed.value:
                return float(parsed.value)
            else:
                return int(parsed.value)
        elif parsed.type == "BOOLEAN":
            return parsed.value == "True"
        elif parsed.type == "IDENTIFIER":
            return parsed.value
        else:
            raise ValueError(f"Cannot evaluate token type: {parsed.type}")

    # Handle function call or operator (list)
    if isinstance(parsed, list) and len(parsed) > 0:
        if isinstance(parsed[0], str):
            # Operator expression: ['OPERATOR', op, left, right]
            if parsed[0] == "OPERATOR" and len(parsed) == 4:
                operator = parsed[1]
                left = evaluate(parsed[2], context, config)
                right = evaluate(parsed[3], context, config)

                # Perform the operation
                if operator == "+":
                    return left + right
                elif operator == "-":
                    return left - right
                elif operator == "*":
                    return left * right
                elif operator == "/":
                    return left / right
                elif operator == "%":
                    return left % right
                elif operator == "^":
                    return left**right
                else:
                    raise ValueError(f"Unknown operator: {operator}")

            # Comparison expression: ['COMPARISON', op, left, right]
            elif parsed[0] == "COMPARISON" and len(parsed) == 4:
                operator = parsed[1]
                left = evaluate(parsed[2], context, config)
                right = evaluate(parsed[3], context, config)

                # Perform comparison
                if operator == "==":
                    return left == right
                elif operator == "!=":
                    return left != right
                elif operator == "<":
                    return left < right
                elif operator == ">":
                    return left > right
                elif operator == "<=":
                    return left <= right
                elif operator == ">=":
                    return left >= right
                else:
                    raise ValueError(f"Unknown comparison operator: {operator}")

            # Logical expression: ['LOGICAL', op, left, right]
            elif parsed[0] == "LOGICAL" and len(parsed) == 4:
                operator = parsed[1]
                left = evaluate(parsed[2], context, config)
                right = evaluate(parsed[3], context, config)

                # Perform logical operation
                if operator == "and":
                    return left and right
                elif operator == "or":
                    return left or right
                else:
                    raise ValueError(f"Unknown logical operator: {operator}")

            # Unary not: ['NOT', operand]
            elif parsed[0] == "NOT" and len(parsed) == 2:
                operand = evaluate(parsed[1], context, config)
                return not operand

            # Function call: [func_name, arg1, arg2, ...]
            else:
                func_name = parsed[0]
                args = [evaluate(arg, context, config) for arg in parsed[1:]]

                # Use the execute function from functions module to handle function calls
                # This uses the FUNCTIONS registry and handles type conversion
                # Pass config to access custom functions
                return functions.execute(func_name, *args, config=config)

    # Return as-is if we can't evaluate
    return parsed


def interpret(
    line: str, context: Dict[str, Any], config: Optional[DRLConfig] = None
) -> Any:
    """Interpret a DRL expression against a context dictionary.

    Args:
        line: The DRL expression string
        context: The data dictionary to resolve references from
        config: Optional DRLConfig for custom syntax symbols (ref_indicator, key_delimiter)

    Returns:
        The result of evaluating the expression

    Examples:
        >>> interpret('$root>timestamp', {'root': {'timestamp': 1234}})
        1234
        >>> interpret('split($data>names, ",")', {'data': {'names': 'a,b,c'}})
        ['a', 'b', 'c']
        >>> interpret('2 + 3 * 4', {})
        14
        >>> interpret('$value * 2 + 10', {'value': 5})
        20
        >>> # Using custom symbols
        >>> interpret('@root.timestamp', {'root': {'timestamp': 1234}}, DRLConfig('@', '.'))
        1234
    """
    if config is None:
        config = DEFAULT_CONFIG

    parsed = parse_line(line, config)
    return evaluate(parsed, context, config)


def interpret_dict(
    expressions: Dict[str, str],
    context: Dict[str, Any],
    config: Optional[DRLConfig] = None,
) -> Dict[str, Any]:
    """Interpret multiple DRL expressions from a dictionary.

    Args:
        expressions: A dictionary mapping keys to DRL expression strings
        context: The data dictionary to resolve references from
        config: Optional DRLConfig for custom syntax symbols
    Returns:
        A dictionary mapping keys to evaluated results
    """
    results = {}
    for key, expr in expressions.items():
        if isinstance(expr, dict):
            # Recursively handle nested dictionaries
            results[key] = interpret_dict(expr, context, config)
        elif isinstance(expr, list):
            # Handle lists of expressions
            results[key] = [
                interpret(item, context, config) if isinstance(item, str) else item
                for item in expr
            ]
        else:
            # Interpret single expressions
            results[key] = interpret(expr, context, config)
    return results
