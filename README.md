# Actual Transaction Importer

Import transactions from [finance-api](https://github.com/benfl3713/finance-api) into [Actual Budget](https://github.com/actualbudget/actual).

## Features

- 🔄 Automatically fetch transactions from finance-api
- 💰 Import transactions into Actual Budget
- 🔍 Duplicate detection (skips already imported transactions)
- 🗺️ Configurable account mapping between systems
- 🔒 Secure credential management via environment variables
- 📅 Date range filtering for imports
- 🧪 Dry-run mode for testing without actual imports

## Prerequisites

- Python 3.8 or higher
- Access to a running [finance-api](https://github.com/benfl3713/finance-api) instance
- Access to an [Actual Budget](https://github.com/actualbudget/actual) server

## Installation

1. Clone the repository:
```bash
git clone https://github.com/benfl3713/actual_transaction_importer.git
cd actual_transaction_importer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

4. Edit `.env` with your configuration:
```bash
# Finance API Configuration
FINANCE_API_URL=http://your-finance-api-url:5000
FINANCE_API_KEY=your_api_key_here  # Optional if your API requires authentication

# Actual Budget Configuration
ACTUAL_SERVER_URL=http://your-actual-server:5006
ACTUAL_PASSWORD=your_actual_password
ACTUAL_BUDGET_ID=your_budget_id
ACTUAL_ENCRYPTION_KEY=your_encryption_key  # Optional if budget is encrypted

# Account Mapping (optional)
# Map finance-api account IDs to Actual Budget account IDs
ACCOUNT_MAPPING=finance_account_id1:actual_account_id1,finance_account_id2:actual_account_id2
```

## Usage

### Basic Import

Import transactions from the last 30 days:
```bash
python main.py
```

### Import with Date Range

Import transactions for a specific date range:
```bash
python main.py --start-date 2024-01-01 --end-date 2024-01-31
```

### Dry Run Mode

Test the import without actually importing transactions:
```bash
python main.py --dry-run
```

This will show you what would be imported without making any changes to your Actual Budget.

### Sync Accounts

Display accounts from both systems to help configure account mapping:
```bash
python main.py --sync-accounts
```

This will list all accounts from both the finance API and Actual Budget, showing their IDs and names. Use this information to configure the `ACCOUNT_MAPPING` in your `.env` file.

### Verbose Logging

Enable detailed logging for troubleshooting:
```bash
python main.py --verbose
```

## Configuration Details

### Account Mapping

If your finance-api account IDs don't match your Actual Budget account IDs, you can configure a mapping in the `.env` file:

```bash
ACCOUNT_MAPPING=finance_id1:actual_id1,finance_id2:actual_id2
```

To find the correct IDs:
1. Run `python main.py --sync-accounts`
2. Note the account IDs from both systems
3. Add the mapping to your `.env` file

### Finding Your Actual Budget ID

Your Budget ID can be found in the Actual Budget UI:
1. Open Actual Budget
2. Go to Settings → Show Advanced Settings
3. Your Budget ID will be displayed

## How It Works

1. **Fetch**: The importer connects to your finance-api and retrieves transactions
2. **Transform**: Transactions are transformed from finance-api format to Actual Budget format
3. **Filter**: The importer checks for duplicates using the `imported_id` field
4. **Import**: New transactions are imported into Actual Budget

## Transaction Field Mapping

The importer maps fields from finance-api to Actual Budget as follows:

| Finance API Field | Actual Budget Field |
|------------------|---------------------|
| id / transactionId | imported_id |
| date / transactionDate | date |
| amount | amount (converted to cents) |
| description / payee | payee_name |
| notes | notes |
| accountId | account_id (via mapping) |

## Troubleshooting

### Connection Errors

If you get connection errors:
- Verify your API URLs are correct and accessible
- Check that your finance-api is running
- Check that your Actual Budget server is running
- Verify your credentials in the `.env` file

### No Transactions Imported

If no transactions are imported:
- Check the date range - transactions might be outside the specified range
- Verify account mapping is configured correctly
- Run with `--dry-run` to see what would be imported
- Enable `--verbose` logging to see detailed error messages

### Duplicate Transactions

The importer automatically skips transactions that have already been imported based on the `imported_id` field. If you see duplicates:
- The transactions might have different IDs in the source system
- Check if transactions were manually created in Actual Budget (these won't have an `imported_id`)

## Development

### Project Structure

```
.
├── main.py                 # Main entry point
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── finance_api_client.py  # Finance API client
│   ├── actual_client.py    # Actual Budget client
│   └── importer.py         # Main importer logic
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment configuration
└── README.md              # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source. See the repository for license details.

## Acknowledgments

- [finance-api](https://github.com/benfl3713/finance-api) - Source of transaction data
- [Actual Budget](https://github.com/actualbudget/actual) - Personal finance management
- [actual-py](https://github.com/actualbudget/actual-py) - Python library for Actual Budget
- [actual-flow](https://github.com/lunchflow/actual-flow) - Inspiration for this project
