"""Demo of the drop_empty feature in interpolate_dict.

This example shows how the drop_empty configuration option can be used
to exclude None values from the resulting dictionary.
"""

from drlang import interpolate_dict, DRLConfig


def demo_drop_empty_false():
    """Show default behavior - None values are kept."""
    print("=" * 70)
    print("Example 1: Default behavior (drop_empty=False)")
    print("=" * 70)

    expressions = {
        "name": "$user>name",
        "email": "$user>email",
        "phone": "$[user>phone]",  # Optional - may be None
        "address": "$[user>address]",  # Optional - may be None
        "age": "$user>age",
    }

    context = {
        "user": {
            "name": "Alice",
            "email": "alice@example.com",
            "age": 30,
            # phone and address are missing
        }
    }

    # Default config - None values are kept
    result = interpolate_dict(expressions, context)

    print("\nExpressions:", expressions)
    print("\nContext:", context)
    print("\nResult:")
    for key, value in result.items():
        print(f"  {key}: {value!r}")
    print()


def demo_drop_empty_true():
    """Show drop_empty behavior - None values are excluded."""
    print("=" * 70)
    print("Example 2: With drop_empty=True")
    print("=" * 70)

    expressions = {
        "name": "$user>name",
        "email": "$user>email",
        "phone": "$[user>phone]",  # Optional - may be None
        "address": "$[user>address]",  # Optional - may be None
        "age": "$user>age",
    }

    context = {
        "user": {
            "name": "Alice",
            "email": "alice@example.com",
            "age": 30,
            # phone and address are missing
        }
    }

    # With drop_empty=True, None values are excluded
    config = DRLConfig(drop_empty=True)
    result = interpolate_dict(expressions, context, config)

    print("\nExpressions:", expressions)
    print("\nContext:", context)
    print("\nResult (None values excluded):")
    for key, value in result.items():
        print(f"  {key}: {value!r}")
    print("\nNote: 'phone' and 'address' keys are not in the result")
    print()


def demo_api_response_cleaning():
    """Practical example: Clean API responses."""
    print("=" * 70)
    print("Example 3: API Response Cleaning")
    print("=" * 70)

    # Transform and clean API data
    expressions = {
        "id": "$user>id",
        "full_name": "$user>name",
        "contact_email": "$[user>email]",
        "phone_number": "$[user>phone]",
        "verified": "$[user>verified]",
        "premium": "$[user>premium]",
        "bio": "$[user>bio]",
    }

    # Simulate multiple users with different optional fields
    users_data = [
        {
            "user": {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "verified": True,
            }
        },
        {
            "user": {
                "id": 2,
                "name": "Bob",
                "phone": "555-1234",
                "premium": True,
            }
        },
        {
            "user": {
                "id": 3,
                "name": "Charlie",
                "email": "charlie@example.com",
                "phone": "555-5678",
                "verified": True,
                "premium": False,
                "bio": "Software engineer",
            }
        },
    ]

    config = DRLConfig(drop_empty=True)

    print("\nProcessing users with drop_empty=True:")
    print("(Only present fields will be included)")
    print()

    for user_context in users_data:
        result = interpolate_dict(expressions, user_context, config)
        print(f"User {result['id']}:")
        for key, value in result.items():
            if key != "id":
                print(f"  {key}: {value!r}")
        print()


def demo_falsy_values_preserved():
    """Show that falsy values (0, False, empty string) are NOT dropped."""
    print("=" * 70)
    print("Example 4: Falsy Values Are Preserved")
    print("=" * 70)

    expressions = {
        "count": "$stats>count",
        "enabled": "$stats>enabled",
        "message": "$stats>message",
        "optional": "$[stats>optional]",  # This will be None
        "score": "$stats>score",
    }

    context = {
        "stats": {
            "count": 0,  # Falsy but NOT None
            "enabled": False,  # Falsy but NOT None
            "message": "",  # Falsy but NOT None
            "score": 42,
        }
    }

    config = DRLConfig(drop_empty=True)
    result = interpolate_dict(expressions, context, config)

    print("\nContext:", context)
    print("\nResult with drop_empty=True:")
    for key, value in result.items():
        print(f"  {key}: {value!r}")
    print("\nNote: Only 'optional' (None) is dropped.")
    print("Falsy values like 0, False, and '' are kept.")
    print()


def demo_nested_dicts():
    """Show drop_empty working with nested dictionaries."""
    print("=" * 70)
    print("Example 5: Nested Dictionaries")
    print("=" * 70)

    expressions = {
        "user": {
            "id": "$id",
            "name": "$name",
            "contact": {
                "email": "$[email]",
                "phone": "$[phone]",
                "address": "$[address]",
            },
            "settings": {
                "theme": "$[settings>theme]",
                "notifications": "$[settings>notifications]",
            },
        }
    }

    context = {
        "id": 123,
        "name": "Alice",
        "settings": {
            "theme": "dark",
        },
    }

    config = DRLConfig(drop_empty=True)
    result = interpolate_dict(expressions, context, config)

    print("\nContext:", context)
    print("\nResult with drop_empty=True (nested):")
    print("  user:")
    print(f"    id: {result['user']['id']}")
    print(f"    name: {result['user']['name']!r}")
    print(f"    contact: {result['user']['contact']}")
    print(f"    settings: {result['user']['settings']}")
    print("\nNote: Empty nested dicts are preserved, but keys with None are excluded.")
    print()


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 12 + "DRLang interpolate_dict drop_empty Demo" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    demo_drop_empty_false()
    demo_drop_empty_true()
    demo_api_response_cleaning()
    demo_falsy_values_preserved()
    demo_nested_dicts()

    print("=" * 70)
    print("Demo complete!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
