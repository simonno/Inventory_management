"""Unit tests for argument parsing logic in bot handlers (no Telegram API calls)."""

import pytest
from bot.utils.formatting import split_message, format_condition_flag, VALID_STATUSES


def test_split_message_short():
    assert split_message("hello") == ["hello"]


def test_split_message_long():
    long_text = ("line\n" * 1000)
    chunks = split_message(long_text, limit=4096)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 4096


def test_format_condition_flag_good():
    assert format_condition_flag("Good") == ""


def test_format_condition_flag_bad():
    assert "⚠️" in format_condition_flag("Laundry Damage")


def test_valid_statuses_list():
    assert "in stock" in VALID_STATUSES
    assert "out to bride" in VALID_STATUSES


def test_days_argument_parsing():
    # Simulates the /orders handler days parsing logic
    def parse_days(arg):
        try:
            val = int(arg)
            if val <= 0:
                raise ValueError
            return val
        except ValueError:
            return None

    assert parse_days("30") == 30
    assert parse_days("abc") is None
    assert parse_days("-5") is None
