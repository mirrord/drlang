from typing import Any, Dict, List, Union, Optional, Callable
import drlang.functions as functions


class DRLError(Exception):
    """Base exception class for DRL parsing and evaluation errors."""

    def __init__(
        self, message: str, expression: str = "", position: int = -1, context: str = ""
    ):
        """Initialize a DRL error with detailed context.

        Args:
            message: The error message
            expression: The full expression being parsed
            position: Position in the expression where error occurred
            context: Additional context about what was being done
        """
        self.message = message
        self.expression = expression
        self.position = position
        self.context = context
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format a detailed error message with context."""
        parts = [self.message]

        if self.expression:
            parts.append(f"\n  Expression: {self.expression}")

            if self.position >= 0 and self.position < len(self.expression):
                # Show pointer to error position
                parts.append(f"  Position {self.position}:")
                # Show surrounding context (up to 40 chars on each side)
                start = max(0, self.position - 40)
                end = min(len(self.expression), self.position + 40)
                snippet = self.expression[start:end]
                pointer_pos = self.position - start

                parts.append(f"    {snippet}")
                parts.append(f"    {' ' * pointer_pos}^")

        if self.context:
            parts.append(f"  Context: {self.context}")

        return "\n".join(parts)


class DRLSyntaxError(DRLError):
    """Exception raised for syntax errors during parsing."""

    pass


class DRLNameError(DRLError):
    """Exception raised when a name (function or reference) is not found."""

    pass


class DRLTypeError(DRLError):
    """Exception raised for type-related errors."""

    pass


class DRLReferenceError(DRLError):
    """Exception raised when a reference path cannot be resolved."""

    pass


class DRLConfig:
    """Configuration for DRL syntax symbols."""

    def __init__(
        self,
        ref_indicator: str = "$",
        key_delimiter: str = ">",
        custom_functions: Optional[Dict[str, Callable]] = None,
        drop_empty: bool = False,
    ):
        """Initialize DRL configuration.

        Args:
            ref_indicator: Symbol to indicate data references (default: '$')
            key_delimiter: Symbol to separate nested keys (default: '>')
            custom_functions: Optional dict of custom functions to register {name: Callable}
            drop_empty: If True, interpolate_dict will exclude keys with None values (default: False)
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
        self.drop_empty = drop_empty


# Default configuration
DEFAULT_CONFIG = DRLConfig()


class Token:
    """Represents a token in a DRL expression."""

    def __init__(self, type_: str, value: str, behavior: str = "required"):
        self.type = type_
        self.value = value
        self.behavior = behavior  # For REFERENCE tokens: 'required' (), 'optional' [], 'passthrough' {}

    def __repr__(self):
        if self.type == "REFERENCE" and hasattr(self, "behavior"):
            return f"Token({self.type}, {self.value!r}, behavior={self.behavior})"
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

    Raises:
        DRLSyntaxError: For invalid syntax during tokenization
    """
    if config is None:
        config = DEFAULT_CONFIG

    tokens = []
    i = 0
    original_expression = expression  # Keep for error reporting

    while i < len(expression):
        # Skip whitespace
        if expression[i].isspace():
            i += 1
            continue

        # Data reference: {ref_indicator}(path) or {ref_indicator}[path] or {ref_indicator}{path}
        # () = required (throw exception), [] = optional (return None), {} = passthrough (return original)
        if expression[i] == config.ref_indicator:
            ref_start = i
            i += 1  # Skip the $ character

            # Determine behavior based on delimiter after $
            behavior = "required"  # Default
            closing_delimiter = None

            if i < len(expression):
                if expression[i] == "(":
                    behavior = "required"
                    closing_delimiter = ")"
                    i += 1  # Skip opening delimiter
                elif expression[i] == "[":
                    behavior = "optional"
                    closing_delimiter = "]"
                    i += 1  # Skip opening delimiter
                elif expression[i] == "{":
                    behavior = "passthrough"
                    closing_delimiter = "}"
                    i += 1  # Skip opening delimiter

            ref = ""
            # Collect reference path until closing delimiter or stop chars
            if closing_delimiter:
                # Parse until closing delimiter
                while i < len(expression) and expression[i] != closing_delimiter:
                    ref += expression[i]
                    i += 1
                if i >= len(expression):
                    raise DRLSyntaxError(
                        f"Unterminated reference: expected closing '{closing_delimiter}'",
                        original_expression,
                        ref_start,
                        f"Reference started at position {ref_start} but never closed",
                    )
                i += 1  # Skip closing delimiter
            else:
                # Old-style reference without delimiters (for backward compatibility)
                # Collect reference path (can include spaces in keys)
                # Stop at operators, comparison operators, delimiters, and quotes
                base_stop_chars = "(),'\"+-*/%^<>=![]{}"
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
                                if (
                                    next_char.isspace()
                                    or next_char in "=!<>(),'\"+-*/%^"
                                ):
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
                            if (
                                j + 2 <= len(expression)
                                and expression[j : j + 2] == "or"
                            ):
                                if (
                                    j + 2 == len(expression)
                                    or not expression[j + 2].isalnum()
                                ):
                                    break

                    ref += expression[i]
                    i += 1
            tokens.append(Token("REFERENCE", ref.strip(), behavior=behavior))
            continue

        # String literal
        if expression[i] in "\"'":
            quote = expression[i]
            quote_start = i
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
            if i >= len(expression):
                raise DRLSyntaxError(
                    f"Unterminated string literal starting with {quote}",
                    original_expression,
                    quote_start,
                    f"String started at position {quote_start} but never closed",
                )
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
            raise DRLSyntaxError(
                "Unexpected '!' character - did you mean '!=' for not-equal comparison?",
                original_expression,
                i,
                "The '!' character is only valid as part of the '!=' operator",
            )

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
        if not expression[i].isspace():
            raise DRLSyntaxError(
                f"Unexpected character '{expression[i]}'",
                original_expression,
                i,
                "This character is not valid DRL syntax",
            )
        i += 1

    return tokens


def resolve_reference(
    reference: str,
    context: Dict[str, Any],
    config: Optional[DRLConfig] = None,
    expression: str = "",
    position: int = -1,
    behavior: str = "required",
    original_ref: str = "",
) -> Any:
    """Resolve a data reference like 'root>timestamp' from context dict.

    Args:
        reference: The reference path (e.g., 'root>timestamp')
        context: The data dictionary to resolve from
        config: Optional DRLConfig with custom key delimiter
        expression: The full expression being parsed (for error reporting)
        position: Position in expression (for error reporting)
        behavior: How to handle missing keys - 'required' (raise error), 'optional' (return None), 'passthrough' (return original string)
        original_ref: The original reference string for passthrough behavior

    Returns:
        The resolved value, None if optional and key not found, or original string if passthrough and key not found

    Raises:
        DRLReferenceError: If the reference path doesn't exist (and behavior is 'required')
        DRLTypeError: If trying to navigate into a non-dict value (and behavior is 'required')
    """
    if config is None:
        config = DEFAULT_CONFIG

    parts = reference.split(config.key_delimiter)
    value = context
    path_so_far = []

    for part in parts:
        part = part.strip()
        path_so_far.append(part)

        if isinstance(value, dict):
            if part not in value:
                if behavior == "optional":
                    return None  # Return None for optional references
                elif behavior == "passthrough":
                    return original_ref  # Return original string for passthrough references
                # behavior == "required" - raise error
                available_keys = list(value.keys())[:5]  # Show up to 5 keys
                key_hint = (
                    f"Available keys: {available_keys}"
                    if available_keys
                    else "Dictionary is empty"
                )
                raise DRLReferenceError(
                    f"Reference key '{part}' not found in context",
                    expression,
                    position,
                    f"Failed at: {config.key_delimiter.join(path_so_far)}\n  {key_hint}",
                )
            value = value[part]
        elif isinstance(value, (list, tuple)):
            # Support list/tuple indexing with integer keys
            try:
                index = int(part)
                if -len(value) <= index < len(value):
                    value = value[index]
                else:
                    if behavior == "optional":
                        return None
                    elif behavior == "passthrough":
                        return original_ref
                    raise DRLReferenceError(
                        f"List index {index} out of range",
                        expression,
                        position,
                        f"List at '{config.key_delimiter.join(path_so_far[:-1])}' has length {len(value)}",
                    )
            except ValueError:
                # Not an integer - can't index list with non-integer
                if behavior == "optional":
                    return None
                elif behavior == "passthrough":
                    return original_ref
                raise DRLTypeError(
                    f"Cannot use non-integer key '{part}' to index {type(value).__name__}",
                    expression,
                    position,
                    f"Value at '{config.key_delimiter.join(path_so_far[:-1])}' is a {type(value).__name__}, requires integer index",
                )
        else:
            if behavior == "optional":
                return None  # Return None for optional references
            elif behavior == "passthrough":
                return original_ref  # Return original string for passthrough references
            # behavior == "required" - raise error
            raise DRLTypeError(
                f"Cannot navigate into non-dict/non-list value at key '{part}'",
                expression,
                position,
                f"Value at '{config.key_delimiter.join(path_so_far[:-1])}' is {type(value).__name__}, not a dictionary or list",
            )

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

    Raises:
        DRLSyntaxError: For syntax errors during parsing
    """
    if config is None:
        config = DEFAULT_CONFIG

    original_line = line  # Keep for error reporting
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
            raise DRLSyntaxError(
                "Unexpected end of expression",
                original_line,
                len(original_line) - 1,
                "Expected a value, reference, or function call",
            )

        token = tokens[start]

        # Parenthesized expression
        if token.type == "LPAREN":
            start += 1
            expr, start = parse_expression_with_precedence(tokens, start)
            if start >= len(tokens) or tokens[start].type != "RPAREN":
                raise DRLSyntaxError(
                    "Missing closing parenthesis ')'",
                    original_line,
                    len(original_line) - 1,
                    "Every opening '(' must have a matching closing ')'",
                )
            start += 1
            return expr, start

        # Function call
        if token.type == "FUNCTION":
            func_name = token.value
            start += 1

            # Expect LPAREN
            if start >= len(tokens) or tokens[start].type != "LPAREN":
                raise DRLSyntaxError(
                    f"Expected '(' after function name '{func_name}'",
                    original_line,
                    -1,
                    f"Function calls must be followed by parentheses: {func_name}(...)",
                )
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
                raise DRLSyntaxError(
                    f"Missing closing parenthesis for function '{func_name}'",
                    original_line,
                    len(original_line) - 1,
                    f"Function call started but never closed: {func_name}(...)",
                )
            start += 1

            return [func_name] + args, start

        # Simple value (reference, string, number, or identifier)
        return token, start + 1

    result, _ = parse_expression_with_precedence(tokens)
    return result


def evaluate(
    parsed,
    context: Dict[str, Any],
    config: Optional[DRLConfig] = None,
    expression: str = "",
) -> Any:
    """Evaluate a parsed DRL expression.

    Args:
        parsed: Result from parse_line()
        context: The data dictionary
        config: Optional DRLConfig with custom syntax symbols
        expression: The original expression (for error reporting)

    Returns:
        The evaluated result

    Raises:
        DRLReferenceError: If a reference cannot be resolved
        DRLNameError: If a function is not found
        DRLTypeError: For type-related errors
    """
    if config is None:
        config = DEFAULT_CONFIG

    # Handle Token directly
    if isinstance(parsed, Token):
        if parsed.type == "REFERENCE":
            # Pass the behavior from the token
            behavior = getattr(parsed, "behavior", "required")
            # Construct original reference string for passthrough behavior
            original_ref = f"{config.ref_indicator}{parsed.value}"
            return resolve_reference(
                parsed.value, context, config, expression, -1, behavior, original_ref
            )
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
            raise DRLSyntaxError(
                f"Cannot evaluate token type: {parsed.type}",
                expression,
                -1,
                f"Token with value '{parsed.value}' has unexpected type",
            )

    # Handle function call or operator (list)
    if isinstance(parsed, list) and len(parsed) > 0:
        if isinstance(parsed[0], str):
            # Operator expression: ['OPERATOR', op, left, right]
            if parsed[0] == "OPERATOR" and len(parsed) == 4:
                operator = parsed[1]
                try:
                    left = evaluate(parsed[2], context, config, expression)
                    right = evaluate(parsed[3], context, config, expression)
                except (TypeError, ValueError):
                    try:
                        left = evaluate(parsed[2], context, config, expression)
                    except Exception as e:
                        raise DRLTypeError(
                            f"Error evaluating left operand: {str(e)}",
                            expression,
                            -1,
                            "Left operand evaluation failed",
                        )

                    try:
                        right = evaluate(parsed[3], context, config, expression)
                    except Exception as e:
                        raise DRLTypeError(
                            f"Error evaluating right operand: {str(e)}",
                            expression,
                            -1,
                            "Right operand evaluation failed",
                        )

                    raise DRLTypeError(
                        f"Type error in operation: {left} {operator} {right}",
                        expression,
                        -1,
                        f"Cannot perform '{operator}' on {type(left).__name__} and {type(right).__name__}",
                    )

                # Perform the operation
                if operator == "+":
                    return left + right
                elif operator == "-":
                    return left - right
                elif operator == "*":
                    return left * right
                elif operator == "/":
                    if right == 0:
                        raise DRLTypeError(
                            "Division by zero", expression, -1, "Cannot divide by zero"
                        )
                    return left / right
                elif operator == "%":
                    if right == 0:
                        raise DRLTypeError(
                            "Modulo by zero",
                            expression,
                            -1,
                            "Cannot perform modulo with zero divisor",
                        )
                    return left % right
                elif operator == "^":
                    return left**right
                else:
                    raise DRLSyntaxError(
                        f"Unknown operator: {operator}",
                        expression,
                        -1,
                        f"The operator '{operator}' is not supported",
                    )

            # Comparison expression: ['COMPARISON', op, left, right]
            elif parsed[0] == "COMPARISON" and len(parsed) == 4:
                operator = parsed[1]
                left = evaluate(parsed[2], context, config, expression)
                right = evaluate(parsed[3], context, config, expression)

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
                    raise DRLSyntaxError(
                        f"Unknown comparison operator: {operator}",
                        expression,
                        -1,
                        f"The comparison operator '{operator}' is not supported",
                    )

            # Logical expression: ['LOGICAL', op, left, right]
            elif parsed[0] == "LOGICAL" and len(parsed) == 4:
                operator = parsed[1]
                left = evaluate(parsed[2], context, config, expression)
                right = evaluate(parsed[3], context, config, expression)

                # Perform logical operation
                if operator == "and":
                    return left and right
                elif operator == "or":
                    return left or right
                else:
                    raise DRLSyntaxError(
                        f"Unknown logical operator: {operator}",
                        expression,
                        -1,
                        f"The logical operator '{operator}' is not supported",
                    )

            # Unary not: ['NOT', operand]
            elif parsed[0] == "NOT" and len(parsed) == 2:
                operand = evaluate(parsed[1], context, config, expression)
                return not operand

            # Function call: [func_name, arg1, arg2, ...]
            else:
                func_name = parsed[0]
                try:
                    args = [
                        evaluate(arg, context, config, expression) for arg in parsed[1:]
                    ]
                except Exception as e:
                    # Re-raise DRL errors as-is
                    if isinstance(e, DRLError):
                        raise
                    # Wrap other errors
                    raise DRLTypeError(
                        f"Error evaluating argument for function '{func_name}': {str(e)}",
                        expression,
                        -1,
                        f"Function: {func_name}",
                    )

                # Use the execute function from functions module to handle function calls
                # This uses the FUNCTIONS registry and handles type conversion
                # Pass config to access custom functions
                try:
                    return functions.execute(func_name, *args, config=config)
                except NameError as e:
                    raise DRLNameError(
                        str(e),
                        expression,
                        -1,
                        f"Function '{func_name}' is not defined. Check spelling or register as custom function.",
                    )
                except Exception as e:
                    # Re-raise DRL errors as-is
                    if isinstance(e, DRLError):
                        raise
                    raise DRLTypeError(
                        f"Error executing function '{func_name}': {str(e)}",
                        expression,
                        -1,
                        f"Function: {func_name}, Arguments: {args}",
                    )

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

    Raises:
        DRLSyntaxError: For syntax errors in the expression
        DRLReferenceError: If a reference path cannot be resolved
        DRLNameError: If a function is not found
        DRLTypeError: For type-related errors

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

    try:
        parsed = parse_line(line, config)
        return evaluate(parsed, context, config, line)
    except DRLError:
        # Re-raise DRL errors as-is (they already have context)
        raise
    except KeyError as e:
        # Convert KeyError to DRLReferenceError
        raise DRLReferenceError(
            f"Reference error: {str(e)}", line, -1, "Key not found in context"
        )
    except Exception as e:
        # Wrap unexpected errors with context
        raise DRLError(
            f"Unexpected error: {str(e)}", line, -1, f"Error type: {type(e).__name__}"
        )


def interpolate_dict(
    templates: Dict[str, Any],
    context: Dict[str, Any],
    config: Optional[DRLConfig] = None,
) -> Dict[str, Any]:
    """Interpolate multiple template strings from a dictionary.

    Args:
        templates: A dictionary mapping keys to template strings or nested dictionaries/lists
        context: The data dictionary to resolve references from
        config: Optional DRLConfig for custom syntax symbols (includes drop_empty flag)

    Returns:
        A dictionary mapping keys to interpolated strings (excludes None values if config.drop_empty is True)
    """
    if config is None:
        config = DEFAULT_CONFIG

    results = {}
    for key, template in templates.items():
        if isinstance(template, dict):
            # Recursively handle nested dictionaries
            value = interpolate_dict(template, context, config)
        elif isinstance(template, list):
            # Handle lists of templates
            value = [
                interpolate(item, context, config) if isinstance(item, str) else item
                for item in template
            ]
        elif isinstance(template, str):
            # Interpolate single template strings
            value = interpolate(template, context, config)
        else:
            # Pass through non-string values unchanged
            value = template

        # Only include in results if not None, or if drop_empty is False
        if not config.drop_empty or value is not None:
            results[key] = value

    return results


def interpolate(
    template: str, context: Dict[str, Any], config: Optional[DRLConfig] = None
) -> str:
    """Interpolate a template string, treating content as literal unless specially marked.

    Content is treated as a literal string UNLESS:
    1. Wrapped in {% expression %} - the expression is evaluated and result inserted
    2. Preceded by a reference indicator (e.g., $ref>path) - the reference is resolved

    Multiple interpolation sequences can be included in a single string, with
    content between them remaining static (literal).

    Args:
        template: The template string with optional interpolation sequences
        context: The data dictionary to resolve references from
        config: Optional DRLConfig for custom syntax symbols

    Returns:
        The interpolated string with all expressions evaluated and references resolved

    Raises:
        DRLSyntaxError: For syntax errors in expressions
        DRLReferenceError: If a reference path cannot be resolved
        DRLNameError: If a function is not found
        DRLTypeError: For type-related errors

    Examples:
        >>> interpolate('Hello, world!', {})
        'Hello, world!'
        >>> interpolate('Value is $value', {'value': 42})
        'Value is 42'
        >>> interpolate('Sum is {% 2 + 3 %}', {})
        'Sum is 5'
        >>> interpolate('Hello $name, you have {% $count * 2 %} items', {'name': 'Alice', 'count': 5})
        'Hello Alice, you have 10 items'
        >>> interpolate('Path: $data>nested>value', {'data': {'nested': {'value': 'found'}}})
        'Path: found'
    """
    if config is None:
        config = DEFAULT_CONFIG

    ref_indicator = config.ref_indicator
    result = []
    i = 0
    template_len = len(template)

    while i < template_len:
        # Check for {% expression %} block
        if template[i : i + 2] == "{%":
            # Find the closing %}
            start_pos = i
            i += 2  # Skip {%

            # Skip leading whitespace
            while i < template_len and template[i].isspace():
                i += 1

            # Find the closing %}
            expr_start = i
            depth = 1
            while i < template_len:
                if template[i : i + 2] == "{%":
                    depth += 1
                    i += 2
                elif template[i : i + 2] == "%}":
                    depth -= 1
                    if depth == 0:
                        break
                    i += 2
                else:
                    i += 1

            if depth != 0:
                raise DRLSyntaxError(
                    "Unterminated expression block: expected closing '%}'",
                    template,
                    start_pos,
                    "Expression block started with '{%' but never closed",
                )

            # Extract and evaluate the expression
            expr = template[expr_start:i].rstrip()
            i += 2  # Skip %}

            try:
                value = interpret(expr, context, config)
                result.append(str(value) if value is not None else "")
            except DRLError:
                raise
            except Exception as e:
                raise DRLError(
                    f"Error evaluating expression: {str(e)}",
                    template,
                    start_pos,
                    f"Expression: {expr}",
                )
            continue

        # Check for reference indicator (e.g., $ref>path)
        if template[i : i + len(ref_indicator)] == ref_indicator:
            start_pos = i
            i += len(ref_indicator)

            # Check for behavior modifiers: (), [], {}
            behavior = "required"
            closing_delimiter = None

            if i < template_len:
                if template[i] == "(":
                    behavior = "required"
                    closing_delimiter = ")"
                    i += 1
                elif template[i] == "[":
                    behavior = "optional"
                    closing_delimiter = "]"
                    i += 1
                elif template[i] == "{":
                    behavior = "passthrough"
                    closing_delimiter = "}"
                    i += 1

            # Collect the reference path
            ref_path = ""

            if closing_delimiter:
                # Parse until closing delimiter
                while i < template_len and template[i] != closing_delimiter:
                    ref_path += template[i]
                    i += 1
                if i >= template_len:
                    raise DRLSyntaxError(
                        f"Unterminated reference: expected closing '{closing_delimiter}'",
                        template,
                        start_pos,
                        f"Reference started at position {start_pos} but never closed",
                    )
                i += 1  # Skip closing delimiter
            else:
                # Collect reference path until stop characters
                key_delimiter = config.key_delimiter
                # Stop at whitespace, operators, and other special chars
                # but allow key_delimiter within reference
                stop_chars = " \t\n\r(),'\"+-*/%^<>=![]{};"
                stop_chars += ref_indicator  # Stop at next reference

                while i < template_len:
                    char = template[i]

                    # Allow key_delimiter within reference
                    if char == key_delimiter[0]:
                        # Check for multi-char delimiter
                        if template[i : i + len(key_delimiter)] == key_delimiter:
                            ref_path += key_delimiter
                            i += len(key_delimiter)
                            continue

                    # Stop at stop characters (but not key_delimiter)
                    if char in stop_chars:
                        break

                    ref_path += char
                    i += 1

            ref_path = ref_path.strip()

            if ref_path:
                # Build original reference string for passthrough behavior
                if closing_delimiter:
                    delim_open = {"required": "(", "optional": "[", "passthrough": "{"}
                    original_ref = f"{ref_indicator}{delim_open[behavior]}{ref_path}{closing_delimiter}"
                else:
                    original_ref = f"{ref_indicator}{ref_path}"

                try:
                    value = resolve_reference(
                        ref_path,
                        context,
                        config,
                        template,
                        start_pos,
                        behavior,
                        original_ref,
                    )
                    result.append(str(value) if value is not None else "")
                except DRLError:
                    raise
            else:
                # Empty reference - just include the indicator as literal
                result.append(ref_indicator)
            continue

        # Regular character - add as literal
        result.append(template[i])
        i += 1

    return "".join(result)
