# Quick Start Guide

Get up and running with the transaction importer in 5 minutes!

## 1. Install (1 minute)

```bash
# Clone the repository
git clone https://github.com/benfl3713/actual_transaction_importer.git
cd actual_transaction_importer

# Install dependencies
pip install -r requirements.txt
```

## 2. Configure (2 minutes)

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your details
nano .env  # or use your preferred editor
```

Minimum required configuration:
```bash
FINANCE_API_URL=http://your-finance-api:5000
FINANCE_API_USERNAME=your_username
FINANCE_API_PASSWORD=your_password
ACTUAL_SERVER_URL=http://your-actual-server:5006
ACTUAL_PASSWORD=your_password
ACTUAL_BUDGET_ID=your_budget_id
```

## 3. Test (1 minute)

```bash
# Verify configuration
python main.py --sync-accounts

# Test import without making changes
python main.py --dry-run
```

## 4. Import (1 minute)

```bash
# Import transactions for the last 30 days
python main.py

# Or specify a date range
python main.py --start-date 2024-01-01 --end-date 2024-01-31
```

## That's it! 🎉

Your transactions should now be in Actual Budget.

## Next Steps

- **Set up account mapping** if your account IDs don't match (see README.md)
- **Schedule regular imports** using cron or Docker (see TESTING.md)
- **Customize field mappings** if needed (see CUSTOMIZATION.md)

## Need Help?

- 📖 [Full documentation](README.md)
- 🧪 [Testing guide](TESTING.md)
- 🔧 [Customization guide](CUSTOMIZATION.md)
- 💡 [Example code](example.py)
- 🐛 [Report issues](https://github.com/benfl3713/actual_transaction_importer/issues)

## Common Issues

**Can't connect to services?**
- Verify URLs are correct
- Ensure services are running
- Check firewall/network settings

**No transactions imported?**
- Check date range
- Verify account mapping
- Use `--dry-run --verbose` to debug

**Wrong amounts or dates?**
- See [CUSTOMIZATION.md](CUSTOMIZATION.md) for field mapping options
