# this module contains the functions available in DRL scripts.
import builtins
import inspect
import re
from typing import Any, get_type_hints, get_origin, Callable


def print_value(*args: Any) -> None:
    """Print values to stdout (named print_value to avoid conflict with built-in print).

    This is aliased as 'print' in DRL expressions.

    Args:
        *args: Values to print
    """
    builtins.print(*args)


# Alias for use in DRL expressions
print = print_value


def if_function(condition: bool, true_value: Any, false_value: Any) -> Any:
    """Conditional function - returns true_value if condition is True, else false_value.

    Args:
        condition: Boolean condition to test
        true_value: Value to return if condition is True
        false_value: Value to return if condition is False

    Returns:
        true_value if condition else false_value

    Examples:
        if(True, 'yes', 'no')  -> 'yes'
        if(False, 100, 200)     -> 200
        if($score > 50, 'pass', 'fail')  -> 'pass' or 'fail' depending on score
    """
    return true_value if condition else false_value


# Regex functions
def regex_search(pattern: str, string: str) -> bool:
    """Search for pattern in string. Returns True if found, False otherwise.

    Args:
        pattern: Regular expression pattern
        string: String to search in

    Returns:
        True if pattern is found, False otherwise

    Examples:
        regex_search(r'\\d+', 'abc123')  -> True
        regex_search(r'^hello', 'hello world')  -> True
    """
    return re.search(pattern, string) is not None


def regex_match(pattern: str, string: str) -> bool:
    """Check if string matches pattern at the beginning. Returns True if matches, False otherwise.

    Args:
        pattern: Regular expression pattern
        string: String to match

    Returns:
        True if string starts with pattern, False otherwise

    Examples:
        regex_match(r'\\d+', '123abc')  -> True
        regex_match(r'\\d+', 'abc123')  -> False
    """
    return re.match(pattern, string) is not None


def regex_findall(pattern: str, string: str) -> list:
    """Find all non-overlapping matches of pattern in string.

    Args:
        pattern: Regular expression pattern
        string: String to search in

    Returns:
        List of all matches

    Examples:
        regex_findall(r'\\d+', 'a1b22c333')  -> ['1', '22', '333']
        regex_findall(r'\\w+', 'hello world')  -> ['hello', 'world']
    """
    return re.findall(pattern, string)


def regex_sub(pattern: str, replacement: str, string: str) -> str:
    """Replace all occurrences of pattern in string with replacement.

    Args:
        pattern: Regular expression pattern
        replacement: Replacement string
        string: String to perform substitution on

    Returns:
        String with all replacements made

    Examples:
        regex_sub(r'\\d+', 'X', 'a1b22c333')  -> 'aXbXcX'
        regex_sub(r'\\s+', '_', 'hello  world')  -> 'hello_world'
    """
    return re.sub(pattern, replacement, string)


def regex_split(pattern: str, string: str) -> list:
    """Split string by occurrences of pattern.

    Args:
        pattern: Regular expression pattern
        string: String to split

    Returns:
        List of substrings

    Examples:
        regex_split(r'\\s+', 'hello  world  test')  -> ['hello', 'world', 'test']
        regex_split(r'[,;]', 'a,b;c')  -> ['a', 'b', 'c']
    """
    return re.split(pattern, string)


def regex_extract(pattern: str, string: str, group: int = 0) -> str:
    """Extract the first match of pattern from string.

    Args:
        pattern: Regular expression pattern
        string: String to search in
        group: Group number to extract (default 0 for entire match)

    Returns:
        Matched string or empty string if not found

    Examples:
        regex_extract(r'\\d+', 'abc123def')  -> '123'
        regex_extract(r'(\\w+)@(\\w+)', 'user@domain', 1)  -> 'user'
    """
    match = re.search(pattern, string)
    if match:
        return match.group(group)
    return ""


FUNCTIONS = {
    "print": print_value,
    "if": if_function,
    "add": sum,
    "len": len,
    "max": max,
    "min": min,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "upper": str.upper,
    "lower": str.lower,
    "capitalize": str.capitalize,
    "strip": str.strip,
    "replace": str.replace,
    "find": str.find,
    "join": str.join,
    "split": str.split,
    "randint": __import__("random").randint,
    "random": __import__("random").random,
    "uniform": __import__("random").uniform,
    "randrange": __import__("random").randrange,
    "choice": __import__("random").choice,
    "shuffle": __import__("random").shuffle,
    "datetime": __import__("datetime").datetime,
    "date": __import__("datetime").date,
    "time": __import__("datetime").time,
    "timedelta": __import__("datetime").timedelta,
    "strptime": __import__("datetime").datetime.strptime,
    "strftime": __import__("datetime").datetime.strftime,
    "all": all,
    "any": any,
    # Regex functions
    "regex_search": regex_search,
    "regex_match": regex_match,
    "regex_findall": regex_findall,
    "regex_sub": regex_sub,
    "regex_split": regex_split,
    "regex_extract": regex_extract,
}


def convert_arg_types(function, *args) -> list:
    """
    Convert argument types based on the function's expected input types.

    Args:
        function: The function to inspect for type hints
        *args: Arguments to convert

    Returns:
        List of converted arguments
    """
    # If no args, return empty list
    if not args:
        return []

    try:
        # Try to get the function signature
        sig = inspect.signature(function)
        params = list(sig.parameters.values())

        # Try to get type hints
        try:
            type_hints = get_type_hints(function)
        except Exception:
            type_hints = {}

        converted = []

        for i, arg in enumerate(args):
            # If we have a parameter at this position
            if i < len(params):
                param = params[i]
                param_name = param.name

                # Skip *args and **kwargs parameters
                if param.kind in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                ):
                    # For variadic args, just pass through
                    converted.append(arg)
                    continue

                # Check if we have a type hint for this parameter
                if param_name in type_hints:
                    expected_type = type_hints[param_name]

                    # Handle generic types (like List, Dict, etc.)
                    origin = get_origin(expected_type)
                    if origin is not None:
                        expected_type = origin

                    # Try to convert if not already the expected type
                    if not isinstance(arg, expected_type):
                        try:
                            converted.append(expected_type(arg))
                        except (TypeError, ValueError):
                            # If conversion fails, use original arg
                            converted.append(arg)
                    else:
                        converted.append(arg)
                # Check annotation directly on parameter
                elif param.annotation != inspect.Parameter.empty:
                    expected_type = param.annotation

                    # Handle generic types
                    origin = get_origin(expected_type)
                    if origin is not None:
                        expected_type = origin

                    # Try to convert if not already the expected type
                    if not isinstance(arg, expected_type):
                        try:
                            converted.append(expected_type(arg))
                        except (TypeError, ValueError):
                            # If conversion fails, use original arg
                            converted.append(arg)
                    else:
                        converted.append(arg)
                else:
                    # No type hint, pass through as-is
                    converted.append(arg)
            else:
                # More args than parameters (variadic case), pass through
                converted.append(arg)

        return converted

    except (ValueError, TypeError):
        # If we can't inspect the function (e.g., built-in), pass args through
        return list(args)


def execute(function_name, *args, config=None):
    """Execute a function by name with the given arguments.

    Args:
        function_name: Name of the function to execute
        *args: Arguments to pass to the function
        config: Optional DRLConfig containing custom functions

    Returns:
        Result of the function call

    Raises:
        NameError: If the function is not found
    """
    # Check custom functions first (if config provided)
    if (
        config
        and hasattr(config, "custom_functions")
        and function_name in config.custom_functions
    ):
        func = config.custom_functions[function_name]
        converted_args = convert_arg_types(func, *args)
        return func(*converted_args)

    # Fall back to built-in functions
    if function_name not in FUNCTIONS:
        raise NameError(f"Function '{function_name}' not found")
    func = FUNCTIONS[function_name]
    converted_args = convert_arg_types(func, *args)
    return func(*converted_args)


def register_function(name: str, func: Callable, config=None):
    """Register a custom function for use in DRL expressions.

    Args:
        name: Name to register the function under
        func: The callable function to register
        config: Optional DRLConfig to add function to. If None, adds to global FUNCTIONS

    Returns:
        The DRLConfig object (if provided) for method chaining

    Examples:
        # Register globally
        register_function('double', lambda x: x * 2)

        # Register to specific config
        config = DRLConfig()
        register_function('triple', lambda x: x * 3, config)
    """
    if config is not None:
        if not hasattr(config, "custom_functions"):
            config.custom_functions = {}
        config.custom_functions[name] = func
        return config
    else:
        FUNCTIONS[name] = func
        return None
