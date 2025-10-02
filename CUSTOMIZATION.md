# Finance API Integration Guide

This guide explains how to customize the transaction importer for your specific finance-api setup.

## Understanding the Finance API

The importer is designed to work with [benfl3713/finance-api](https://github.com/benfl3713/finance-api). However, the exact response format may vary based on your configuration and version.

## Customizing Transaction Field Mapping

The transaction transformation happens in `src/importer.py` in the `transform_transaction` method. You may need to adjust this based on your finance-api response format.

### Default Field Mapping

The importer currently expects these fields from finance-api:

```python
{
    "id": "unique_transaction_id",           # or "transactionId"
    "accountId": "account_identifier",       # Account ID
    "date": "2024-01-15",                    # or "transactionDate", ISO format
    "amount": 50.00,                         # Transaction amount
    "type": "debit",                         # "debit" or "credit"
    "description": "Payee Name",             # or "payee"
    "notes": "Optional notes"                # Optional
}
```

### Common Customizations

#### 1. Different Field Names

If your finance-api uses different field names, update the `transform_transaction` method:

```python
# In src/importer.py, around line 62-80

# Example: If your API uses "merchant" instead of "description"
"payee_name": finance_transaction.get("merchant", finance_transaction.get("description", "Unknown")),

# Example: If your API uses "transactionAmount" instead of "amount"
amount = finance_transaction.get("transactionAmount", 0)

# Example: If your API uses "transactionCategory" for type
transaction_type = finance_transaction.get("transactionCategory", "").lower()
```

#### 2. Different Amount Formats

Some APIs return amounts in cents (integer), others as decimal strings:

```python
# If amount is in cents (e.g., 5000 for $50.00)
amount = finance_transaction.get("amount", 0) / 100

# If amount is a string
amount = float(finance_transaction.get("amount", "0"))
```

#### 3. Different Transaction Type Logic

Adjust the logic for determining if a transaction is income or expense:

```python
# Current logic (lines 70-74)
transaction_type = finance_transaction.get("type", "").lower()
if transaction_type == "debit" and amount > 0:
    amount = -amount
elif transaction_type == "credit" and amount < 0:
    amount = abs(amount)

# Alternative: If type is "expense" or "income"
transaction_type = finance_transaction.get("type", "").lower()
if transaction_type == "expense" and amount > 0:
    amount = -amount
elif transaction_type == "income" and amount < 0:
    amount = abs(amount)

# Alternative: If negative amounts mean expenses
# Just use the amount as-is
amount = finance_transaction.get("amount", 0)
```

#### 4. Date Format Variations

Handle different date formats:

```python
from datetime import datetime

# Current handling (line 62-65)
date = finance_transaction.get("date", finance_transaction.get("transactionDate"))
if isinstance(date, str) and "T" in date:
    date = date.split("T")[0]  # ISO format: 2024-01-15T10:30:00

# Alternative: Handle different formats
date_str = finance_transaction.get("date")
if date_str:
    # Try ISO format
    if "T" in date_str:
        date = date_str.split("T")[0]
    # Try MM/DD/YYYY format
    elif "/" in date_str:
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        date = date_obj.strftime("%Y-%m-%d")
    # Try DD-MM-YYYY format
    elif "-" in date_str and len(date_str.split("-")[0]) == 2:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        date = date_obj.strftime("%Y-%m-%d")
    else:
        date = date_str
```

## Testing Your Customizations

After making changes, always test with a dry run:

```bash
python main.py --dry-run --verbose
```

This will show you the transformed transactions without importing them.

## Example: Full Custom Transformation

Here's a complete example of a customized `transform_transaction` method:

```python
def transform_transaction(
    self,
    finance_transaction: Dict[str, Any],
    account_mapping: Dict[str, str]
) -> Optional[Dict[str, Any]]:
    """Transform transaction from finance API to Actual Budget format."""
    
    # Get account ID
    finance_account_id = str(finance_transaction.get("bankAccountId", ""))
    
    # Map to Actual account ID
    if account_mapping and finance_account_id not in account_mapping:
        logger.warning(f"No mapping found for account ID: {finance_account_id}")
        return None
    
    actual_account_id = account_mapping.get(finance_account_id) if account_mapping else finance_account_id
    
    # Parse date - custom format
    date_str = finance_transaction.get("transactionDate")
    date_obj = datetime.strptime(date_str, "%Y%m%d")  # Format: YYYYMMDD
    date = date_obj.strftime("%Y-%m-%d")
    
    # Parse amount - in cents
    amount = finance_transaction.get("amountInCents", 0) / 100
    
    # Determine if expense or income
    is_debit = finance_transaction.get("isDebit", True)
    if is_debit and amount > 0:
        amount = -amount
    
    # Get merchant name
    merchant = finance_transaction.get("merchantName", "Unknown")
    
    # Combine notes
    category = finance_transaction.get("category", "")
    reference = finance_transaction.get("referenceNumber", "")
    notes = f"{category} - {reference}".strip(" -")
    
    return {
        "account_id": actual_account_id,
        "date": date,
        "amount": amount,
        "payee_name": merchant,
        "notes": notes,
        "imported_id": str(finance_transaction.get("transactionId", ""))
    }
```

## Debugging Tips

### 1. Log the Raw Transaction

Add logging to see the raw transaction data:

```python
def transform_transaction(self, finance_transaction: Dict[str, Any], ...):
    logger.debug(f"Raw transaction: {finance_transaction}")
    # ... rest of the method
```

### 2. Test with a Single Transaction

Create a test script:

```python
from src.finance_api_client import FinanceAPIClient
from src.importer import TransactionImporter
from src.config import Config

config = Config()
client = FinanceAPIClient(config.FINANCE_API_URL, config.FINANCE_API_USERNAME, config.FINANCE_API_PASSWORD)

# Get just one transaction
transactions = client.get_all_transactions()
if transactions:
    print("Sample transaction from API:")
    print(transactions[0])
    
    # Test transformation
    importer = TransactionImporter(config)
    transformed = importer.transform_transaction(transactions[0], {})
    print("\nTransformed transaction:")
    print(transformed)
```

### 3. Use Python Debugger

Add a breakpoint in the transform method:

```python
def transform_transaction(self, finance_transaction: Dict[str, Any], ...):
    import pdb; pdb.set_trace()  # Breakpoint
    # ... rest of the method
```

## Contributing Your Customizations

If you've customized the importer for a specific finance-api configuration, consider contributing:

1. Document your changes
2. Make them configurable if possible
3. Submit a pull request

## Getting Help

If you're having trouble customizing the importer:

1. Check the finance-api documentation for the response format
2. Use `--dry-run --verbose` to see what's happening
3. Look at the raw API response
4. Open an issue with your API response format (remove sensitive data)
