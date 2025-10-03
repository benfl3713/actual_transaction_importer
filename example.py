#!/usr/bin/env python3
"""
Example usage of the transaction importer.

This script demonstrates how to use the transaction importer
both as a standalone script and as a library.
"""
import logging
from datetime import datetime, timedelta
from src.importer import TransactionImporter
from src.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def example_basic_import():
    """Example: Basic import for the last 30 days."""
    logger.info("Example 1: Basic import for the last 30 days")
    
    importer = TransactionImporter()
    
    # Calculate dates
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Run import
    stats = importer.import_transactions(
        start_date=start_date,
        end_date=end_date
    )
    
    logger.info(f"Import completed: {stats}")


def example_dry_run():
    """Example: Dry run to see what would be imported."""
    logger.info("Example 2: Dry run to preview transactions")
    
    importer = TransactionImporter()
    
    stats = importer.import_transactions(
        start_date="2024-01-01",
        end_date="2024-01-31",
        dry_run=True
    )
    
    logger.info(f"Dry run completed: {stats}")


def example_sync_accounts():
    """Example: Display accounts from both systems."""
    logger.info("Example 3: Sync accounts to help with mapping")
    
    importer = TransactionImporter()
    importer.sync_accounts()


def example_custom_config():
    """Example: Using custom configuration."""
    logger.info("Example 4: Using custom configuration")
    
    # Create custom config
    config = Config()
    config.FINANCE_API_URL = "http://localhost:5000"
    config.ACTUAL_SERVER_URL = "http://localhost:5006"
    
    # Validate config before using
    try:
        config.validate()
        importer = TransactionImporter(config)
        # ... use importer
    except ValueError as e:
        logger.error(f"Configuration error: {e}")


if __name__ == "__main__":
    print("This is an example file demonstrating library usage.")
    print("To actually run imports, use main.py")
    print("\nExample commands:")
    print("  python main.py --dry-run")
    print("  python main.py --sync-accounts")
    print("  python main.py --start-date 2024-01-01 --end-date 2024-01-31")
    print("\nSee README.md for full documentation.")
