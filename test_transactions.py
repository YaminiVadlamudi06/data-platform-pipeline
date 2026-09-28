import logging

import pytest

from transactions import process_transactions, validate_transaction


def test_sales_and_refunds():
    transactions = [
        {
            "transaction_id": "T1",
            "event_id": "E100",
            "amount": 200,
            "status": "PURCHASED"
        },
        {
            "transaction_id": "T2",
            "event_id": "E100",
            "amount": 100,
            "status": "REFUNDED"
        }
    ]

    result = process_transactions(transactions)

    assert result["E100"]["gross_sales"] == 200
    assert result["E100"]["refunds"] == 100
    assert result["E100"]["net_sales"] == 100

def make_tx(**overrides):
    tx = {
        "transaction_id": "T1",
        "event_id": "E100",
        "amount": 200,
        "status": "PURCHASED"
    }
    tx.update(overrides)
    return tx


def test_valid_transaction_passes_validation():
    assert validate_transaction(make_tx()) is None


def test_zero_amount_is_valid():
    assert validate_transaction(make_tx(amount=0)) is None


@pytest.mark.parametrize("value", [None, ""])
def test_rejects_empty_transaction_id(value):
    assert validate_transaction(make_tx(transaction_id=value)) == "missing transaction_id"


@pytest.mark.parametrize("value", [None, ""])
def test_rejects_empty_event_id(value):
    assert validate_transaction(make_tx(event_id=value)) == "missing event_id"


def test_rejects_missing_transaction_id():
    tx = make_tx()
    del tx["transaction_id"]
    valid = make_tx(transaction_id="T2", amount=50)

    result = process_transactions([tx, valid])

    assert result == {"E100": {"gross_sales": 50, "refunds": 0, "net_sales": 50}}


def test_rejects_missing_event_id():
    tx = make_tx()
    del tx["event_id"]
    valid = make_tx(transaction_id="T2", amount=50)

    result = process_transactions([tx, valid])

    assert result == {"E100": {"gross_sales": 50, "refunds": 0, "net_sales": 50}}


def test_rejects_negative_amount():
    invalid = make_tx(event_id="E200", amount=-10)
    valid = make_tx(transaction_id="T2", amount=50)

    result = process_transactions([invalid, valid])

    assert "E200" not in result
    assert result["E100"]["gross_sales"] == 50


@pytest.mark.parametrize("status", ["CANCELLED", "purchased", None])
def test_rejects_invalid_status(status):
    invalid = make_tx(event_id="E200", status=status)
    valid = make_tx(transaction_id="T2", amount=50)

    result = process_transactions([invalid, valid])

    assert "E200" not in result
    assert result["E100"]["gross_sales"] == 50


def test_rejected_transaction_is_not_marked_as_seen():
    invalid = make_tx(amount=-10)
    valid = make_tx(amount=75)

    result = process_transactions([invalid, valid])

    assert result["E100"]["gross_sales"] == 75


def test_duplicate_valid_transaction_is_still_skipped():
    result = process_transactions([make_tx(), make_tx()])

    assert result["E100"]["gross_sales"] == 200


def test_rejection_is_logged(caplog):
    with caplog.at_level(logging.WARNING, logger="transactions"):
        process_transactions([make_tx(amount=-10)])

    assert "negative amount" in caplog.text
