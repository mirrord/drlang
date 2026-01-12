# SPDX-FileCopyrightText: 2026-present Dane Howard <mirrord@gmail.com>
#
# SPDX-License-Identifier: MIT
# import pytest
from drlang.functions import print_value, execute


class TestSplitFunction:
    """Test the split function."""

    def test_split_comma(self):
        result = execute("split", "a,b,c", ",")
        assert result == ["a", "b", "c"]

    def test_split_space(self):
        result = execute("split", "hello world test", " ")
        assert result == ["hello", "world", "test"]

    def test_split_custom_separator(self):
        result = execute("split", "apple|banana|cherry", "|")
        assert result == ["apple", "banana", "cherry"]

    def test_split_no_separator(self):
        result = execute("split", "noseparator", ",")
        assert result == ["noseparator"]

    def test_split_empty_string(self):
        result = execute("split", "", ",")
        assert result == [""]

    def test_split_multiple_chars_separator(self):
        result = execute("split", "one::two::three", "::")
        assert result == ["one", "two", "three"]


class TestPrintFunction:
    """Test the print function."""

    def test_print_single_value(self, capsys):
        print_value("hello")
        captured = capsys.readouterr()
        assert captured.out == "hello\n"

    def test_print_multiple_values(self, capsys):
        print_value("hello", "world")
        captured = capsys.readouterr()
        assert captured.out == "hello world\n"

    def test_print_number(self, capsys):
        print_value(42)
        captured = capsys.readouterr()
        assert captured.out == "42\n"

    def test_print_alias(self, capsys):
        """Test that 'print' is properly aliased."""
        execute("print", "test")
        captured = capsys.readouterr()
        assert captured.out == "test\n"

    def test_print_returns_none(self):
        result = print_value("test")
        assert result is None
