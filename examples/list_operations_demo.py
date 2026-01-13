"""Demo showcasing DRLang's list operations and iteration functions.

This example demonstrates:
- List indexing in references
- List manipulation functions
- Iteration functions (map, filter, reduce)
- Chaining operations
"""

from drlang.language import interpret


def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def demo_list_indexing():
    """Demonstrate list indexing through references."""
    print_section("List Indexing")

    data = {
        "items": ["apple", "banana", "cherry"],
        "matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        "users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
    }

    # Basic indexing
    print("\nBasic list indexing:")
    print(f"  Data: {data['items']}")
    print(f"  $items>0 = {interpret('$items>0', data)}")
    print(f"  $items>2 = {interpret('$items>2', data)}")

    # Nested lists
    print("\nNested list access:")
    print(f"  Data: {data['matrix']}")
    print(f"  $matrix>1>1 = {interpret('$matrix>1>1', data)}")
    print(f"  $matrix>0>2 = {interpret('$matrix>0>2', data)}")

    # Lists in dicts
    print("\nAccessing dict fields in lists:")
    print(f"  Data: {data['users']}")
    print(f"  $users>0>name = {interpret('$users>0>name', data)}")
    print(f"  $users>1>age = {interpret('$users>1>age', data)}")

    # Negative indexing (via variables)
    data["neg_one"] = -1
    print("\nNegative indexing (using list_get function):")
    print(f"  $neg_one = {data['neg_one']}")
    print(
        f"  list_get($items, $neg_one) = {interpret('list_get($items, $neg_one)', data)}"
    )


def demo_list_functions():
    """Demonstrate list manipulation functions."""
    print_section("List Manipulation Functions")

    data = {"nums": [1, 2, 3, 4, 5]}

    # Get with default
    print("\nlist_get - safe list access:")
    print(f"  Data: {data['nums']}")
    print(f"  list_get($nums, 2) = {interpret('list_get($nums, 2)', data)}")
    print(
        f"  list_get($nums, 10, 'N/A') = {interpret('list_get($nums, 10, \"N/A\")', data)}"
    )

    # Slice
    print("\nlist_slice - slice lists:")
    print(f"  list_slice($nums, 1, 4) = {interpret('list_slice($nums, 1, 4)', data)}")
    print(
        f"  list_slice($nums, 0, 5, 2) = {interpret('list_slice($nums, 0, 5, 2)', data)}"
    )

    # Append
    print("\nlist_append - add to list:")
    result = interpret("list_append($nums, 6)", data)
    print(f"  list_append($nums, 6) = {result}")

    # Concat
    data["more"] = [6, 7, 8]
    print("\nlist_concat - merge lists:")
    print(f"  more: {data['more']}")
    print(
        f"  list_concat($nums, $more) = {interpret('list_concat($nums, $more)', data)}"
    )

    # Contains
    print("\nlist_contains - membership test:")
    print(f"  list_contains($nums, 3) = {interpret('list_contains($nums, 3)', data)}")
    print(f"  list_contains($nums, 10) = {interpret('list_contains($nums, 10)', data)}")

    # Index
    print("\nlist_index - find index:")
    print(f"  list_index($nums, 4) = {interpret('list_index($nums, 4)', data)}")
    data["not_found"] = -1
    print(
        f"  list_index($nums, 99, $not_found) = {interpret('list_index($nums, 99, $not_found)', data)}"
    )

    # Reverse
    print("\nlist_reverse - reverse order:")
    print(f"  list_reverse($nums) = {interpret('list_reverse($nums)', data)}")

    # Unique
    data["dupes"] = [1, 2, 2, 3, 1, 4, 3]
    print("\nlist_unique - remove duplicates:")
    print(f"  Data: {data['dupes']}")
    print(f"  list_unique($dupes) = {interpret('list_unique($dupes)', data)}")

    # Flatten
    data["nested"] = [[1, 2], [3, 4], [5]]
    print("\nlist_flatten - flatten one level:")
    print(f"  Data: {data['nested']}")
    print(f"  list_flatten($nested) = {interpret('list_flatten($nested)', data)}")


def demo_map():
    """Demonstrate the map function."""
    print_section("Map Function - Transform Each Element")

    # Simple arithmetic
    data = {"nums": [1, 2, 3, 4]}
    print("\nDouble each number:")
    print(f"  Data: {data['nums']}")
    print(f"  map('$item * 2', $nums) = {interpret('map(\"$item * 2\", $nums)', data)}")

    # String functions
    data = {"words": ["hello", "world", "python"]}
    print("\nUppercase strings:")
    print(f"  Data: {data['words']}")
    print(
        f"  map('upper($item)', $words) = {interpret('map(\"upper($item)\", $words)', data)}"
    )

    # Using index
    data = {"nums": [10, 20, 30]}
    print("\nAdd index to each item:")
    print(f"  Data: {data['nums']}")
    print(
        f"  map('$item + $index', $nums) = {interpret('map(\"$item + $index\", $nums)', data)}"
    )

    # Complex expression
    data = {"nums": [1, 2, 3, 4, 5]}
    print("\nConditional transformation:")
    print(f"  Data: {data['nums']}")
    expression = 'map("if($item > 3, $item * 10, $item)", $nums)'
    print("  map('if($item > 3, $item * 10, $item)', $nums)")
    print(f"  = {interpret(expression, data)}")


def demo_filter():
    """Demonstrate the filter function."""
    print_section("Filter Function - Select Elements")

    # Simple comparison
    data = {"nums": [1, 2, 3, 4, 5, 6]}
    print("\nFilter numbers > 3:")
    print(f"  Data: {data['nums']}")
    print(
        f"  filter('$item > 3', $nums) = {interpret('filter(\"$item > 3\", $nums)', data)}"
    )

    # Even numbers
    print("\nFilter even numbers:")
    print(
        f"  filter('$item % 2 == 0', $nums) = {interpret('filter(\"$item % 2 == 0\", $nums)', data)}"
    )

    # Using index
    print("\nFilter by index (even positions):")
    print(
        f"  filter('$index % 2 == 0', $nums) = {interpret('filter(\"$index % 2 == 0\", $nums)', data)}"
    )

    # String filtering
    data = {"words": ["apple", "banana", "apricot", "cherry"]}
    print("\nFilter strings starting with 'a' (using regex):")
    print(f"  Data: {data['words']}")
    print("  filter('regex_match($item, \"^a\")', $words)")
    print(
        f"  = {interpret('filter(\"regex_match($item, \\\"^a\\\")\", $words)', data)}"
    )


def demo_reduce():
    """Demonstrate the reduce function."""
    print_section("Reduce Function - Accumulate Values")

    # Sum
    data = {"nums": [1, 2, 3, 4, 5]}
    print("\nSum all numbers:")
    print(f"  Data: {data['nums']}")
    print(
        f"  reduce('$acc + $item', $nums) = {interpret('reduce(\"$acc + $item\", $nums)', data)}"
    )

    # With initial value
    print("\nSum with initial value 10:")
    print(
        f"  reduce('$acc + $item', $nums, 10) = {interpret('reduce(\"$acc + $item\", $nums, 10)', data)}"
    )

    # Find max
    print("\nFind maximum:")
    print("  reduce('if($item > $acc, $item, $acc)', $nums)")
    print(f"  = {interpret('reduce(\"if($item > $acc, $item, $acc)\", $nums)', data)}")

    # String concatenation
    data = {"words": ["Hello", "World", "DRLang"]}
    print("\nConcatenate strings:")
    print(f"  Data: {data['words']}")
    print("  reduce('$acc + \" \" + $item', $words)")
    print(f"  = {interpret('reduce(\"$acc + \\\" \\\" + $item\", $words)', data)}")


def demo_chaining():
    """Demonstrate chaining operations."""
    print_section("Chaining Operations")

    data = {"nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

    print("\nPipeline: double → filter > 10 → sum")
    print(f"  Original: {data['nums']}")

    # Step 1: Double
    doubled = interpret('map("$item * 2", $nums)', data)
    print(f"  After map (double): {doubled}")

    # Step 2: Filter
    data["doubled"] = doubled
    filtered = interpret('filter("$item > 10", $doubled)', data)
    print(f"  After filter (> 10): {filtered}")

    # Step 3: Sum
    data["filtered"] = filtered
    total = interpret('reduce("$acc + $item", $filtered)', data)
    print(f"  After reduce (sum): {total}")

    print("\nAnother example: even squares")
    data = {"nums": list(range(1, 11))}
    print(f"  Original: {data['nums']}")

    # Get even numbers
    evens = interpret('filter("$item % 2 == 0", $nums)', data)
    print(f"  Filter even: {evens}")

    # Square them
    data["evens"] = evens
    squares = interpret('map("$item * $item", $evens)', data)
    print(f"  Map to squares: {squares}")

    # Sum
    data["squares"] = squares
    total = interpret('reduce("$acc + $item", $squares)', data)
    print(f"  Sum: {total}")


def demo_practical_examples():
    """Demonstrate practical use cases."""
    print_section("Practical Examples")

    # Process user data
    print("\nExample 1: Process user records")
    data = {
        "users": [
            {"name": "Alice", "age": 30, "score": 85},
            {"name": "Bob", "age": 25, "score": 92},
            {"name": "Charlie", "age": 35, "score": 78},
            {"name": "Diana", "age": 28, "score": 95},
        ]
    }
    print(f"  Users: {len(data['users'])} records")

    # Get all names
    from drlang.functions import map_list

    names = map_list("$item>name", data["users"], {})
    print(f"  Names: {names}")

    # Filter high scorers
    from drlang.functions import filter_list

    high_scorers = filter_list("$item>score >= 90", data["users"], {})
    print(f"  High scorers (>= 90): {[u['name'] for u in high_scorers]}")

    # Calculate average score
    from drlang.functions import reduce_list

    scores = map_list("$item>score", data["users"], {})
    total_score = reduce_list("$acc + $item", scores, 0, {})
    avg_score = total_score / len(scores)
    print(f"  Average score: {avg_score:.2f}")

    # Working with API response
    print("\nExample 2: Transform API response")
    api_data = {
        "results": [
            {"id": 1, "title": "Item A", "price": 10.99},
            {"id": 2, "title": "Item B", "price": 25.50},
            {"id": 3, "title": "Item C", "price": 15.00},
        ]
    }

    # Extract titles
    titles = map_list("$item>title", api_data["results"], {})
    print(f"  Titles: {titles}")

    # Filter by price
    affordable = filter_list("$item>price < 20", api_data["results"], {})
    print(f"  Affordable items (< $20): {[item['title'] for item in affordable]}")

    # Calculate total
    prices = map_list("$item>price", api_data["results"], {})
    total = reduce_list("$acc + $item", prices, 0, {})
    print(f"  Total price: ${total:.2f}")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 60)
    print("  DRLang List Operations & Iteration Functions Demo")
    print("=" * 60)

    demo_list_indexing()
    demo_list_functions()
    demo_map()
    demo_filter()
    demo_reduce()
    demo_chaining()
    demo_practical_examples()

    print("\n" + "=" * 60)
    print("  Demo Complete!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
