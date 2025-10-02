# Testing Guide

This guide helps you test the transaction importer to ensure it works correctly with your setup.

## Prerequisites for Testing

Before you begin testing, ensure you have:

1. **Finance API** running and accessible
   - URL should be accessible (e.g., `http://localhost:5000`)
   - Username and password for authentication
   - At least one account with some transactions

2. **Actual Budget Server** running and accessible
   - URL should be accessible (e.g., `http://localhost:5006`)
   - Valid password for authentication
   - A budget file created with at least one account
   - Budget ID and encryption key (if encrypted)

3. **Python 3.8+** installed

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install in development mode:
```bash
pip install -e .
```

## Step 2: Configure Environment

Copy the example configuration:
```bash
cp .env.example .env
```

Edit `.env` with your actual values:
```bash
# Finance API Configuration
FINANCE_API_URL=http://localhost:5000
FINANCE_API_USERNAME=your_username
FINANCE_API_PASSWORD=your_password

# Actual Budget Configuration
ACTUAL_SERVER_URL=http://localhost:5006
ACTUAL_PASSWORD=your_actual_password
ACTUAL_BUDGET_ID=your_budget_id
ACTUAL_ENCRYPTION_KEY=your_encryption_key  # if encrypted
```

## Step 3: Test Connection to Finance API

Create a test script to verify finance API connectivity:

```python
from src.finance_api_client import FinanceAPIClient
from src.config import Config

config = Config()
client = FinanceAPIClient(config.FINANCE_API_URL, config.FINANCE_API_USERNAME, config.FINANCE_API_PASSWORD)

# Test getting accounts
try:
    accounts = client.get_accounts()
    print(f"✓ Successfully connected to finance API")
    print(f"✓ Found {len(accounts)} accounts")
    for account in accounts:
        print(f"  - {account.get('name', 'N/A')} (ID: {account.get('id', 'N/A')})")
except Exception as e:
    print(f"✗ Error connecting to finance API: {e}")

# Test getting transactions
try:
    transactions = client.get_all_transactions()
    print(f"✓ Successfully fetched transactions")
    print(f"✓ Found {len(transactions)} transactions")
except Exception as e:
    print(f"✗ Error fetching transactions: {e}")
```

## Step 4: Test Connection to Actual Budget

```python
from src.actual_client import ActualBudgetClient
from src.config import Config

config = Config()

try:
    with ActualBudgetClient(
        config.ACTUAL_SERVER_URL,
        config.ACTUAL_PASSWORD,
        config.ACTUAL_BUDGET_ID,
        config.ACTUAL_ENCRYPTION_KEY
    ) as client:
        accounts = client.get_accounts()
        print(f"✓ Successfully connected to Actual Budget")
        print(f"✓ Found {len(accounts)} accounts")
        for account in accounts:
            print(f"  - {account.get('name', 'N/A')} (ID: {account.get('id', 'N/A')})")
except Exception as e:
    print(f"✗ Error connecting to Actual Budget: {e}")
```

## Step 5: Sync Accounts

Use the built-in sync-accounts command to see accounts from both systems:

```bash
python main.py --sync-accounts
```

This will display:
- All accounts from finance API with their IDs
- All accounts from Actual Budget with their IDs

Use this information to configure the `ACCOUNT_MAPPING` in your `.env` file.

## Step 6: Dry Run Test

Test the import without actually importing anything:

```bash
python main.py --dry-run --verbose
```

This will:
- Fetch transactions from finance API
- Transform them for Actual Budget
- Show you what would be imported
- Not actually import anything

Review the output to ensure:
- Transactions are being fetched correctly
- Date format is correct
- Amounts are correct (positive for income, negative for expenses)
- Payee names are populated
- Account mapping is working

## Step 7: Test Import with Small Date Range

Start with a small date range to test the actual import:

```bash
python main.py --start-date 2024-01-01 --end-date 2024-01-01 --verbose
```

This will import transactions for just one day. Check your Actual Budget to verify:
- Transactions were imported
- Amounts are correct
- Dates are correct
- Payees are correct
- No duplicates were created

## Step 8: Test Duplicate Detection

Run the same import command again:

```bash
python main.py --start-date 2024-01-01 --end-date 2024-01-01 --verbose
```

The output should show that transactions were skipped because they already exist.

## Step 9: Full Import

Once you've verified everything works correctly, run a full import:

```bash
python main.py --start-date 2024-01-01 --end-date 2024-12-31
```

Or use the default (last 30 days):

```bash
python main.py
```

## Common Issues and Solutions

### Issue: Connection Refused

**Symptoms:**
```
Error: Connection refused
```

**Solutions:**
- Verify the API URLs are correct
- Ensure the services are running
- Check firewall settings
- Verify network connectivity

### Issue: Authentication Failed

**Symptoms:**
```
Error: 401 Unauthorized
Error: 403 Forbidden
```

**Solutions:**
- Verify your username and password for finance API
- Verify your password for Actual Budget
- Check that credentials haven't expired

### Issue: No Transactions Imported

**Symptoms:**
- Import completes but shows 0 transactions

**Solutions:**
- Check the date range - ensure transactions exist in that range
- Verify account mapping is configured correctly
- Use `--dry-run --verbose` to see what would be imported
- Check the finance API is returning transactions

### Issue: Incorrect Amounts

**Symptoms:**
- Amounts are wrong (positive instead of negative or vice versa)

**Solutions:**
- Check the `type` field in finance API response
- Modify the `transform_transaction` method in `src/importer.py`
- Adjust the amount transformation logic based on your API's format

### Issue: Missing Payee Names

**Symptoms:**
- Payee names show as "Unknown"

**Solutions:**
- Check which field contains the payee/description in finance API
- Update the field mapping in `src/importer.py` in the `transform_transaction` method

## Performance Testing

For large imports:

1. **Test with small batches first** (1 week at a time)
2. **Monitor memory usage** - the importer loads all transactions into memory
3. **Consider rate limiting** - some APIs have rate limits
4. **Use logging** to track progress with `--verbose`

## Automated Testing (Optional)

You can set up automated imports using cron or systemd timers:

### Cron Example
```bash
# Run daily at 3 AM
0 3 * * * cd /path/to/actual_transaction_importer && python main.py
```

### Docker with Cron
See the `docker-compose.example.yml` for a containerized setup.

## Next Steps

After successful testing:

1. Set up automated imports (if desired)
2. Monitor the imports regularly
3. Review imported transactions in Actual Budget
4. Adjust categorization rules in Actual Budget as needed

## Getting Help

If you encounter issues not covered here:

1. Check the main README.md for additional documentation
2. Review the example.py file for usage examples
3. Open an issue on GitHub with:
   - Error messages (with sensitive data removed)
   - Steps to reproduce
   - Your environment (Python version, OS, etc.)
