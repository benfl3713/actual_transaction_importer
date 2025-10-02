"""Client for fetching transactions from the finance API."""
import logging
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class FinanceAPIClient:
    """Client for interacting with the finance API."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the Finance API client.
        
        Args:
            base_url: Base URL of the finance API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """
        Fetch all accounts from the finance API.
        
        Returns:
            List of account dictionaries
        """
        try:
            url = f"{self.base_url}/api/accounts"
            logger.info(f"Fetching accounts from {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            accounts = response.json()
            logger.info(f"Retrieved {len(accounts)} accounts")
            return accounts
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching accounts: {e}")
            raise
    
    def get_transactions(
        self,
        account_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch transactions from the finance API.
        
        Args:
            account_id: Optional account ID to filter transactions
            start_date: Optional start date (YYYY-MM-DD format)
            end_date: Optional end date (YYYY-MM-DD format)
        
        Returns:
            List of transaction dictionaries
        """
        try:
            url = f"{self.base_url}/api/transactions"
            params = {}
            
            if account_id:
                params["accountId"] = account_id
            if start_date:
                params["startDate"] = start_date
            if end_date:
                params["endDate"] = end_date
            
            logger.info(f"Fetching transactions from {url} with params {params}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            transactions = response.json()
            logger.info(f"Retrieved {len(transactions)} transactions")
            return transactions
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching transactions: {e}")
            raise
    
    def get_all_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch all transactions from all accounts.
        
        Args:
            start_date: Optional start date (YYYY-MM-DD format)
            end_date: Optional end date (YYYY-MM-DD format)
        
        Returns:
            List of all transactions
        """
        logger.info("Fetching all transactions")
        return self.get_transactions(start_date=start_date, end_date=end_date)
