"""Main transaction importer module."""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config import Config
from .finance_api_client import FinanceAPIClient
from .actual_client import ActualBudgetClient

logger = logging.getLogger(__name__)


class TransactionImporter:
    """Main class for importing transactions from finance API to Actual Budget."""
    
    def __init__(self, config: Config = None):
        """
        Initialize the transaction importer.
        
        Args:
            config: Configuration object (uses default Config if not provided)
        """
        self.config = config or Config()
        self.config.validate()
        
        self.finance_client = FinanceAPIClient(
            base_url=self.config.FINANCE_API_URL,
            username=self.config.FINANCE_API_USERNAME,
            password=self.config.FINANCE_API_PASSWORD
        )
        
        self.account_mapping = self.config.get_account_mapping()
    
    def transform_transaction(
        self,
        finance_transaction: Dict[str, Any],
        account_mapping: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Transform a transaction from finance API format to Actual Budget format.
        
        Args:
            finance_transaction: Transaction from finance API
            account_mapping: Mapping from finance account IDs to Actual account IDs
        
        Returns:
            Transformed transaction or None if account not mapped
        """
        # Get the finance account ID
        finance_account_id = str(finance_transaction.get("AccountID", ""))
        
        # Map to Actual account ID
        if account_mapping and finance_account_id not in account_mapping:
            logger.warning(f"No mapping found for account ID: {finance_account_id}")
            return None
        
        actual_account_id = account_mapping.get(finance_account_id) if account_mapping else finance_account_id
        
        # Transform the transaction
        # Note: Field names may vary based on the actual finance-api structure
        # Adjust these mappings as needed based on your API's response format
        
        date = finance_transaction.get("Date")
        if isinstance(date, str) and "T" in date:
            # Handle ISO format datetime
            date = date.split("T")[0]
        
        amount = finance_transaction.get("Amount", 0)
        
        
        transformed = {
            "account_id": actual_account_id,
            "date": date,
            "amount": amount,
            "payee_name": finance_transaction.get("Vendor", finance_transaction.get("Merchant", "Unknown")),
            "notes": finance_transaction.get("Note", ""),
            "imported_id": str(finance_transaction.get("ID")),
            "cleared": finance_transaction.get('Status') == 'SETTLED'
        }
        
        return transformed
    
    def import_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, int]:
        """
        Import transactions from finance API to Actual Budget.
        
        Args:
            start_date: Optional start date (YYYY-MM-DD format)
            end_date: Optional end date (YYYY-MM-DD format)
            dry_run: If True, don't actually import, just show what would be imported
        
        Returns:
            Dictionary with import statistics
        """
        logger.info("Starting transaction import process")
        
        # Fetch transactions from finance API
        logger.info("Fetching transactions from finance API")
        finance_transactions = self.finance_client.get_all_transactions(
            start_date=start_date,
            end_date=end_date
        )
        logger.info(f"Fetched {len(finance_transactions)} transactions from finance API")
        
        # Transform transactions
        logger.info("Transforming transactions")
        transformed_transactions = []
        for txn in finance_transactions:
            transformed = self.transform_transaction(txn, self.account_mapping)
            if transformed:
                transformed_transactions.append(transformed)
        
        logger.info(f"Transformed {len(transformed_transactions)} transactions")
        
        if dry_run:
            logger.info("Dry run mode - not importing transactions")
            for txn in transformed_transactions[:5]:  # Show first 5 as sample
                logger.info(f"Would import: {txn}")
            if len(transformed_transactions) > 5:
                logger.info(f"... and {len(transformed_transactions) - 5} more")
            return {"success": 0, "failed": 0, "skipped": 0, "dry_run": len(transformed_transactions)}
        
        # Import into Actual Budget
        logger.info("Importing transactions into Actual Budget")
        with ActualBudgetClient(
            base_url=self.config.ACTUAL_SERVER_URL,
            password=self.config.ACTUAL_PASSWORD,
            budget_id=self.config.ACTUAL_BUDGET_ID,
            encryption_key=self.config.ACTUAL_ENCRYPTION_KEY
        ) as actual_client:
            stats = actual_client.import_transactions(transformed_transactions)
        
        logger.info(f"Import complete: {stats}")
        return stats
    
    def sync_accounts(self) -> None:
        """
        Display accounts from both systems to help with mapping.
        
        This is a helper method to show available accounts from both systems.
        """
        logger.info("Fetching accounts from finance API")
        finance_accounts = self.finance_client.get_accounts()
        
        logger.info("\nFinance API Accounts:")
        for account in finance_accounts:
            logger.info(f"  ID: {account.get('id', 'N/A')}, Name: {account.get('name', 'N/A')}")
        
        logger.info("\nFetching accounts from Actual Budget")
        with ActualBudgetClient(
            base_url=self.config.ACTUAL_SERVER_URL,
            password=self.config.ACTUAL_PASSWORD,
            budget_id=self.config.ACTUAL_BUDGET_ID,
            encryption_key=self.config.ACTUAL_ENCRYPTION_KEY
        ) as actual_client:
            actual_accounts = actual_client.get_accounts()
        
        logger.info("\nActual Budget Accounts:")
        for account in actual_accounts:
            logger.info(f"  ID: {account.get('id', 'N/A')}, Name: {account.get('name', 'N/A')}")
        
        logger.info("\nUse these IDs to configure your ACCOUNT_MAPPING in .env")
        logger.info("Format: ACCOUNT_MAPPING=finance_id1:actual_id1,finance_id2:actual_id2")
