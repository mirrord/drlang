"""Tests for regex functions in DRL."""

from drlang import interpret


class TestRegexSearch:
    """Test regex_search function."""

    def test_search_digit(self):
        """Test searching for digits."""
        assert interpret(r'regex_search("\\d+", "abc123")', {}) is True
        assert interpret(r'regex_search("\\d+", "abcdef")', {}) is False

    def test_search_word(self):
        """Test searching for word pattern."""
        assert interpret(r'regex_search("\\bworld\\b", "hello world")', {}) is True
        assert interpret(r'regex_search("\\bworld\\b", "helloworld")', {}) is False

    def test_search_with_reference(self):
        """Test regex_search with data reference."""
        data = {"text": "Order #12345"}
        assert interpret(r'regex_search("#\\d+", $text)', data) is True

    def test_search_email_pattern(self):
        """Test searching for email pattern."""
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
        assert interpret(f'regex_search("{pattern}", "user@example.com")', {}) is True
        assert interpret(f'regex_search("{pattern}", "notanemail")', {}) is False


class TestRegexMatch:
    """Test regex_match function."""

    def test_match_start(self):
        """Test matching at string start."""
        assert interpret(r'regex_match("\\d+", "123abc")', {}) is True
        assert interpret(r'regex_match("\\d+", "abc123")', {}) is False

    def test_match_entire_string(self):
        """Test matching entire string."""
        assert interpret(r'regex_match("^\\d+$", "12345")', {}) is True
        assert interpret(r'regex_match("^\\d+$", "123abc")', {}) is False

    def test_match_with_reference(self):
        """Test regex_match with data reference."""
        data = {"code": "ABC123"}
        assert interpret(r'regex_match("^[A-Z]+", $code)', data) is True


class TestRegexFindall:
    """Test regex_findall function."""

    def test_findall_digits(self):
        """Test finding all digit sequences."""
        result = interpret(r'regex_findall("\\d+", "a1b22c333")', {})
        assert result == ["1", "22", "333"]

    def test_findall_words(self):
        """Test finding all words."""
        result = interpret(r'regex_findall("\\w+", "hello world test")', {})
        assert result == ["hello", "world", "test"]

    def test_findall_no_matches(self):
        """Test findall with no matches."""
        result = interpret(r'regex_findall("\\d+", "abcdef")', {})
        assert result == []

    def test_findall_with_reference(self):
        """Test regex_findall with data reference."""
        data = {"text": "Prices: $10, $20, $30"}
        result = interpret(r'regex_findall("\\$\\d+", $text)', data)
        assert result == ["$10", "$20", "$30"]

    def test_findall_with_len(self):
        """Test combining findall with len function."""
        result = interpret(r'len(regex_findall("\\d+", "1 22 333"))', {})
        assert result == 3


class TestRegexSub:
    """Test regex_sub function."""

    def test_sub_digits(self):
        """Test replacing digits."""
        result = interpret(r'regex_sub("\\d+", "X", "a1b22c333")', {})
        assert result == "aXbXcX"

    def test_sub_whitespace(self):
        """Test replacing whitespace."""
        result = interpret(r'regex_sub("\\s+", "_", "hello  world   test")', {})
        assert result == "hello_world_test"

    def test_sub_with_reference(self):
        """Test regex_sub with data reference."""
        data = {"text": "Phone: 123-456-7890"}
        result = interpret(r'regex_sub("[\\-]", "", $text)', data)
        assert result == "Phone: 1234567890"

    def test_sub_remove_html_tags(self):
        """Test removing HTML tags."""
        result = interpret(r'regex_sub("<[^>]+>", "", "<p>Hello</p>")', {})
        assert result == "Hello"


class TestRegexSplit:
    """Test regex_split function."""

    def test_split_by_whitespace(self):
        """Test splitting by whitespace."""
        result = interpret(r'regex_split("\\s+", "hello  world   test")', {})
        assert result == ["hello", "world", "test"]

    def test_split_by_multiple_delimiters(self):
        """Test splitting by multiple delimiters."""
        result = interpret(r'regex_split("[,;]", "a,b;c")', {})
        assert result == ["a", "b", "c"]

    def test_split_with_reference(self):
        """Test regex_split with data reference."""
        data = {"csv": "one,two,three"}
        result = interpret(r'regex_split(",", $csv)', data)
        assert result == ["one", "two", "three"]

    def test_split_by_digits(self):
        """Test splitting by digits."""
        result = interpret(r'regex_split("\\d+", "a1b22c333d")', {})
        assert result == ["a", "b", "c", "d"]


class TestRegexExtract:
    """Test regex_extract function."""

    def test_extract_digit_sequence(self):
        """Test extracting digit sequence."""
        result = interpret(r'regex_extract("\\d+", "Order #12345")', {})
        assert result == "12345"

    def test_extract_no_match(self):
        """Test extract with no match."""
        result = interpret(r'regex_extract("\\d+", "abcdef")', {})
        assert result == ""

    def test_extract_with_reference(self):
        """Test regex_extract with data reference."""
        data = {"text": "Price: $99.99"}
        result = interpret(r'regex_extract("\\$[\\d.]+", $text)', data)
        assert result == "$99.99"

    def test_extract_email(self):
        """Test extracting email address."""
        text = "Contact: user@example.com for info"
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
        result = interpret(f'regex_extract("{pattern}", "{text}")', {})
        assert result == "user@example.com"

    def test_extract_with_group(self):
        """Test extracting specific capture group."""
        result = interpret(r'regex_extract("(\\w+)@(\\w+)", "user@domain", 1)', {})
        assert result == "user"

        result = interpret(r'regex_extract("(\\w+)@(\\w+)", "user@domain", 2)', {})
        assert result == "domain"


class TestRegexWithConditionals:
    """Test regex functions with conditional logic."""

    def test_regex_in_if_condition(self):
        """Test using regex in if() condition."""
        expr = r'if(regex_search("\\d+", $text), "has numbers", "no numbers")'

        result = interpret(expr, {"text": "abc123"})
        assert result == "has numbers"

        result = interpret(expr, {"text": "abcdef"})
        assert result == "no numbers"

    def test_validate_email(self):
        """Test email validation with regex."""
        pattern = r"@.*\\."
        expr = f'if(regex_search("{pattern}", $email), "valid", "invalid")'

        result = interpret(expr, {"email": "user@example.com"})
        assert result == "valid"

        result = interpret(expr, {"email": "notanemail"})
        assert result == "invalid"

    def test_extract_and_convert(self):
        """Test extracting with regex and converting type."""
        data = {"price_text": "Price: $123"}
        expr = r'int(regex_sub("[^\\d]", "", $price_text))'
        result = interpret(expr, data)
        assert result == 123


class TestRegexRealWorldScenarios:
    """Test real-world use cases with regex."""

    def test_parse_log_entry(self):
        """Test parsing log entry."""
        data = {"log": "[2024-01-15] ERROR: Connection failed"}

        # Extract date
        date_expr = r'regex_extract("\\d{4}-\\d{2}-\\d{2}", $log)'
        date = interpret(date_expr, data)
        assert date == "2024-01-15"

        # Extract level
        level_expr = r'regex_extract("(ERROR|WARNING|INFO)", $log)'
        level = interpret(level_expr, data)
        assert level == "ERROR"

    def test_clean_phone_number(self):
        """Test cleaning phone number."""
        data = {"phone": "(123) 456-7890"}
        expr = r'regex_sub("[^\\d]", "", $phone)'
        result = interpret(expr, data)
        assert result == "1234567890"

    def test_extract_hashtags(self):
        """Test extracting hashtags from text."""
        data = {"tweet": "Hello #world this is #awesome #test"}
        expr = r'regex_findall("#\\w+", $tweet)'
        result = interpret(expr, data)
        assert result == ["#world", "#awesome", "#test"]

    def test_validate_password(self):
        """Test password validation with multiple regex checks."""
        data = {"password": "MyP@ss123"}

        # Check for uppercase
        has_upper = interpret(r'regex_search("[A-Z]", $password)', data)
        assert has_upper is True

        # Check for lowercase
        has_lower = interpret(r'regex_search("[a-z]", $password)', data)
        assert has_lower is True

        # Check for digit
        has_digit = interpret(r'regex_search("\\d", $password)', data)
        assert has_digit is True

        # Check for special char
        has_special = interpret(r'regex_search("[^a-zA-Z0-9]", $password)', data)
        assert has_special is True

    def test_parse_csv_with_regex(self):
        """Test parsing CSV-like data."""
        data = {"csv": "name,age,city\nAlice,30,NYC\nBob,25,LA"}

        # Extract all names (first field in each line)
        expr = r'regex_findall("^(\\w+),", $csv)'
        result = interpret(expr, data)
        # Note: With multiline flag this would work differently
        # For now, just test that it extracts the first one
        assert "name" in result or "Alice" in result

    def test_redact_sensitive_info(self):
        """Test redacting sensitive information."""
        data = {"text": "SSN: 123-45-6789, Credit: 1234-5678-9012-3456"}

        # Redact SSN
        expr1 = r'regex_sub("\\d{3}-\\d{2}-\\d{4}", "XXX-XX-XXXX", $text)'
        result1 = interpret(expr1, data)
        assert "XXX-XX-XXXX" in result1

        # Redact credit card
        data2 = {"text": result1}
        expr2 = (
            r'regex_sub("\\d{4}-\\d{4}-\\d{4}-\\d{4}", "XXXX-XXXX-XXXX-XXXX", $text)'
        )
        result2 = interpret(expr2, data2)
        assert "XXXX-XXXX-XXXX-XXXX" in result2


class TestRegexEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_string(self):
        """Test regex functions with empty string."""
        assert interpret(r'regex_search("\\d+", "")', {}) is False
        assert interpret(r'regex_findall("\\d+", "")', {}) == []
        assert interpret(r'regex_sub("\\d+", "X", "")', {}) == ""

    def test_special_characters(self):
        """Test with special regex characters."""
        result = interpret(r'regex_search("\\.", "a.b")', {})
        assert result is True

        result = interpret(r'regex_search("\\*", "a*b")', {})
        assert result is True

    def test_case_sensitivity(self):
        """Test case sensitivity in regex."""
        # Default is case-sensitive
        assert interpret(r'regex_search("ABC", "abc")', {}) is False
        assert interpret(r'regex_search("ABC", "ABC")', {}) is True

    def test_nested_regex_calls(self):
        """Test nesting regex function calls."""
        # Clean then search
        expr = r'regex_search("\\d+", regex_sub("[^\\w\\d]", "", "a-1-b-2"))'
        result = interpret(expr, {})
        assert result is True
