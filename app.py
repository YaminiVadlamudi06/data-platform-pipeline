from transactions import process_transactions

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
        "status": "PURCHASED"
    },
    {
        "transaction_id": "T3",
        "event_id": "E100",
        "amount": 100,
        "status": "REFUNDED"
    }
]

print(process_transactions(transactions))