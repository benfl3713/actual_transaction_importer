"""Client for importing transactions into Actual Budget."""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from actual import Actual
from actual.queries import get_accounts, create_transaction, get_transactions

logger = logging.getLogger(__name__)


class ActualBudgetClient:
    """Client for interacting with Actual Budget."""
    
    def __init__(
        self,
        base_url: str,
        password: str,
        budget_id: str,
        encryption_key: Optional[str] = None
    ):
        """
        Initialize the Actual Budget client.
        
        Args:
            base_url: Base URL of the Actual Budget server
            password: Password for the Actual Budget server
            budget_id: Budget ID to import transactions into
            encryption_key: Optional encryption key for the budget
        """
        self.base_url = base_url
        self.password = password
        self.budget_id = budget_id
        self.encryption_key = encryption_key
        self.actual = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
    
    def connect(self) -> None:
        """Connect to Actual Budget server."""
        try:
            logger.info(f"Connecting to Actual Budget at {self.base_url}")
            self.actual = Actual(
                base_url=self.base_url,
                password=self.password,
                file=self.budget_id,
                encryption_password=self.encryption_key,
                cert=False
            )
            self.actual.__enter__()
            logger.info("Successfully connected to Actual Budget")
        except Exception as e:
            logger.error(f"Error connecting to Actual Budget: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from Actual Budget server."""
        if self.actual:
            try:
                self.actual.__exit__(None, None, None)
                logger.info("Disconnected from Actual Budget")
            except Exception as e:
                logger.error(f"Error disconnecting from Actual Budget: {e}")
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """
        Get all accounts from Actual Budget.
        
        Returns:
            List of account dictionaries
        """
        try:
            accounts = get_accounts(self.actual.session)
            logger.info(f"Retrieved {len(accounts)} accounts from Actual Budget")
            return [{"id": acc.id, "name": acc.name} for acc in accounts]
        except Exception as e:
            logger.error(f"Error getting accounts: {e}")
            raise
    
    def get_existing_transactions(
        self,
        account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get existing transactions from Actual Budget.
        
        Args:
            account_id: Optional account ID to filter transactions
        
        Returns:
            List of transaction dictionaries
        """
        try:
            transactions = get_transactions(self.actual.session)
            
            if account_id:
                transactions = [t for t in transactions if t.account_id == account_id]
            
            logger.info(f"Retrieved {len(transactions)} existing transactions")
            return transactions
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            raise
    
    def import_transaction(self, transaction: Dict[str, Any]) -> bool:
        """
        Import a single transaction into Actual Budget.
        
        Args:
            transaction: Transaction dictionary with the following fields:
                - account_id: Account ID in Actual Budget
                - date: Transaction date (YYYY-MM-DD or datetime object)
                - amount: Transaction amount (negative for expenses, positive for income)
                - payee_name: Payee name
                - notes: Optional notes
                - imported_id: Optional unique ID from source system
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert date to datetime if it's a string
            date = transaction.get("date")
            if isinstance(date, str):
                date = datetime.strptime(date, "%Y-%m-%d").date()
            
            # Get the amount - Actual expects positive for deposits, negative for payments
            amount = transaction.get("amount", 0)
            
            # Create transaction in Actual Budget
            create_transaction(
                self.actual.session,
                date=date,
                account=transaction["account_id"],
                amount=amount,  # Actual handles it as-is
                payee=transaction.get("payee_name", "Unknown"),
                notes=transaction.get("notes", ""),
                imported_id=transaction.get("imported_id")
            )
            
            logger.debug(f"Imported transaction: {transaction.get('payee_name')} - {transaction.get('amount')}")
            return True
        except Exception as e:
            logger.error(f"Error importing transaction: {e}")
            return False
    
    def import_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Import multiple transactions into Actual Budget.
        
        Args:
            transactions: List of transaction dictionaries
        
        Returns:
            Dictionary with import statistics (success, failed, skipped)
        """
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        # Get existing transactions to avoid duplicates
        existing_ids = set()
        try:
            existing = self.get_existing_transactions()
            existing_ids = {t.imported_id for t in existing if t.imported_id}
        except Exception as e:
            logger.warning(f"Could not fetch existing transactions: {e}")
        
        for transaction in transactions:
            # Skip if already imported
            imported_id = transaction.get("imported_id")
            if imported_id and imported_id in existing_ids:
                logger.debug(f"Skipping duplicate transaction: {imported_id}")
                stats["skipped"] += 1
                continue
            
            if self.import_transaction(transaction):
                stats["success"] += 1
            else:
                stats["failed"] += 1
        
        logger.info(f"Import complete: {stats}")
        self.actual.commit()
        return stats
