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


# List functions
def list_get(lst: list, index: int, default: Any = None) -> Any:
    """Get item from list at index, with optional default value.

    Args:
        lst: List to get item from
        index: Index to retrieve (supports negative indexing)
        default: Default value if index is out of range

    Returns:
        Item at index, or default if index is out of range

    Examples:
        list_get([1, 2, 3], 0)           -> 1
        list_get([1, 2, 3], -1)          -> 3
        list_get([1, 2, 3], 10, 'none')  -> 'none'
    """
    try:
        return lst[index]
    except (IndexError, TypeError):
        return default


def list_slice(lst: list, start: int = None, end: int = None, step: int = 1) -> list:
    """Get a slice of a list.

    Args:
        lst: List to slice
        start: Start index (inclusive, default is beginning)
        end: End index (exclusive, default is end)
        step: Step size (default 1)

    Returns:
        Sliced list

    Examples:
        list_slice([1, 2, 3, 4, 5], 1, 4)     -> [2, 3, 4]
        list_slice([1, 2, 3, 4, 5], 0, 5, 2)  -> [1, 3, 5]
        list_slice([1, 2, 3, 4, 5], 2)        -> [3, 4, 5]
    """
    return lst[start:end:step]


def list_append(lst: list, item: Any) -> list:
    """Append an item to a list (returns new list).

    Args:
        lst: List to append to
        item: Item to append

    Returns:
        New list with item appended

    Examples:
        list_append([1, 2], 3)  -> [1, 2, 3]
    """
    return lst + [item]


def list_concat(lst1: list, lst2: list) -> list:
    """Concatenate two lists.

    Args:
        lst1: First list
        lst2: Second list

    Returns:
        Concatenated list

    Examples:
        list_concat([1, 2], [3, 4])  -> [1, 2, 3, 4]
    """
    return lst1 + lst2


def list_contains(lst: list, item: Any) -> bool:
    """Check if list contains an item.

    Args:
        lst: List to search
        item: Item to search for

    Returns:
        True if item is in list, False otherwise

    Examples:
        list_contains([1, 2, 3], 2)  -> True
        list_contains([1, 2, 3], 5)  -> False
    """
    return item in lst


def list_index(lst: list, item: Any, default: int = -1) -> int:
    """Find the index of an item in a list.

    Args:
        lst: List to search
        item: Item to find
        default: Value to return if item not found (default -1)

    Returns:
        Index of item, or default if not found

    Examples:
        list_index([1, 2, 3], 2)  -> 1
        list_index([1, 2, 3], 5)  -> -1
    """
    try:
        return lst.index(item)
    except ValueError:
        return default


def list_reverse(lst: list) -> list:
    """Reverse a list.

    Args:
        lst: List to reverse

    Returns:
        Reversed list

    Examples:
        list_reverse([1, 2, 3])  -> [3, 2, 1]
    """
    return list(reversed(lst))


def list_unique(lst: list) -> list:
    """Get unique items from a list, preserving order.

    Args:
        lst: List to get unique items from

    Returns:
        List with duplicates removed

    Examples:
        list_unique([1, 2, 2, 3, 1])  -> [1, 2, 3]
    """
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def list_flatten(lst: list) -> list:
    """Flatten a list of lists one level.

    Args:
        lst: List to flatten

    Returns:
        Flattened list

    Examples:
        list_flatten([[1, 2], [3, 4]])  -> [1, 2, 3, 4]
    """
    result = []
    for item in lst:
        if isinstance(item, (list, tuple)):
            result.extend(item)
        else:
            result.append(item)
    return result


def map_list(expression: str, lst: list, context: dict = None) -> list:
    """Apply an expression to each element of a list.

    The current item is available as $item in the expression.
    The current index is available as $index in the expression.

    Args:
        expression: DRLang expression to evaluate for each item
        lst: List to iterate over
        context: Optional additional context data (can pass entire context dict)

    Returns:
        List of results

    Examples:
        map("$item * 2", [1, 2, 3])           -> [2, 4, 6]
        map("upper($item)", ["a", "b"])       -> ["A", "B"]
        map("$item + $index", [10, 20, 30])   -> [10, 21, 32]
    """
    from drlang.language import interpret

    # If context is None, initialize empty dict
    if context is None:
        context = {}
    # If context is a dict, use it; otherwise wrap single values
    elif not isinstance(context, dict):
        context = {"value": context}

    results = []
    for index, item in enumerate(lst):
        # Create context with item and index
        eval_context = {**context, "item": item, "index": index}
        result = interpret(expression, eval_context)
        results.append(result)

    return results


def filter_list(expression: str, lst: list, context: dict = None) -> list:
    """Filter a list using an expression.

    The current item is available as $item in the expression.
    The current index is available as $index in the expression.

    Args:
        expression: DRLang expression that should return a boolean
        lst: List to filter
        context: Optional additional context data

    Returns:
        Filtered list containing only items where expression is true

    Examples:
        filter_list("$item > 2", [1, 2, 3, 4])      -> [3, 4]
        filter_list("$index % 2 == 0", [10, 20, 30, 40])  -> [10, 30]
    """
    from drlang.language import interpret

    if context is None:
        context = {}

    results = []
    for index, item in enumerate(lst):
        # Create context with item and index
        eval_context = {**context, "item": item, "index": index}
        if interpret(expression, eval_context):
            results.append(item)

    return results


def reduce_list(
    expression: str, lst: list, initial: Any = None, context: dict = None
) -> Any:
    """Reduce a list to a single value using an expression.

    The accumulator is available as $acc in the expression.
    The current item is available as $item in the expression.

    Args:
        expression: DRLang expression to combine accumulator and item
        lst: List to reduce
        initial: Initial accumulator value (default: first item of list)
        context: Optional additional context data

    Returns:
        Final accumulated value

    Examples:
        reduce_list("$acc + $item", [1, 2, 3, 4])       -> 10
        reduce_list("$acc + $item", [1, 2, 3], 10)      -> 16
        reduce_list("if($item > $acc, $item, $acc)", [5, 2, 8, 3])  -> 8
    """
    from drlang.language import interpret

    if context is None:
        context = {}

    if not lst:
        return initial

    if initial is None:
        accumulator = lst[0]
        start_index = 1
    else:
        accumulator = initial
        start_index = 0

    for item in lst[start_index:]:
        eval_context = {**context, "acc": accumulator, "item": item}
        accumulator = interpret(expression, eval_context)

    return accumulator


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
    # List functions
    "list_get": list_get,
    "list_slice": list_slice,
    "list_append": list_append,
    "list_concat": list_concat,
    "list_contains": list_contains,
    "list_index": list_index,
    "list_reverse": list_reverse,
    "list_unique": list_unique,
    "list_flatten": list_flatten,
    "map": map_list,
    "filter": filter_list,
    "reduce": reduce_list,
    "sorted": sorted,
    "reversed": list_reverse,  # Alias for consistency
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
