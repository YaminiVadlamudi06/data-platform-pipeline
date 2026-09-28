import logging

logger = logging.getLogger(__name__)

VALID_STATUSES = {"PURCHASED", "REFUNDED"}


def validate_transaction(tx):
    """Return a rejection reason for tx, or None if it is valid."""
    if not tx.get("transaction_id"):
        return "missing transaction_id"

    if not tx.get("event_id"):
        return "missing event_id"

    amount = tx.get("amount")
    if amount is None:
        return "missing amount"
    if amount < 0:
        return "negative amount"

    if tx.get("status") not in VALID_STATUSES:
        return "invalid status"

    return None


def process_transactions(transactions):
    result = {}
    seen = set()

    for tx in transactions:
        reason = validate_transaction(tx)

        if reason is not None:
            logger.warning("Rejected transaction %r: %s", tx, reason)
            continue

        transaction_id = tx["transaction_id"]

        if transaction_id in seen:
            continue

        seen.add(transaction_id)

        event_id = tx["event_id"]
        amount = tx["amount"]
        status = tx["status"]

        if event_id not in result:
            result[event_id] = {
                "gross_sales": 0,
                "refunds": 0,
                "net_sales": 0
            }

        if status == "PURCHASED":
            result[event_id]["gross_sales"] += amount

        elif status == "REFUNDED":
            result[event_id]["refunds"] += amount

        result[event_id]["net_sales"] = (
            result[event_id]["gross_sales"]
            - result[event_id]["refunds"]
        )

    return result
