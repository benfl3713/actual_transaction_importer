#!/usr/bin/env python3
"""Main entry point for the transaction importer."""
import argparse
import logging
import sys
from datetime import datetime, timedelta

from src.importer import TransactionImporter


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration.
    
    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    """Main function to run the transaction importer."""
    parser = argparse.ArgumentParser(
        description="Import transactions from finance API to Actual Budget"
    )
    
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date for transaction import (YYYY-MM-DD). Defaults to 30 days ago."
    )
    
    parser.add_argument(
        "--end-date",
        type=str,
        help="End date for transaction import (YYYY-MM-DD). Defaults to today."
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually importing transactions (useful for testing)"
    )
    
    parser.add_argument(
        "--sync-accounts",
        action="store_true",
        help="Display accounts from both systems to help with mapping"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize the importer
        importer = TransactionImporter()
        
        # Handle sync-accounts command
        if args.sync_accounts:
            logger.info("Syncing accounts...")
            importer.sync_accounts()
            return 0
        
        # Set default dates if not provided
        start_date = args.start_date
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            logger.info(f"No start date provided, using: {start_date}")
        
        end_date = args.end_date
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
            logger.info(f"No end date provided, using: {end_date}")
        
        # Run the import
        logger.info(f"Importing transactions from {start_date} to {end_date}")
        if args.dry_run:
            logger.info("DRY RUN MODE - No transactions will be imported")
        
        stats = importer.import_transactions(
            start_date=start_date,
            end_date=end_date,
            dry_run=args.dry_run
        )
        
        # Print summary
        logger.info("\n" + "=" * 50)
        logger.info("IMPORT SUMMARY")
        logger.info("=" * 50)
        for key, value in stats.items():
            logger.info(f"{key.upper()}: {value}")
        logger.info("=" * 50)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during import: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
