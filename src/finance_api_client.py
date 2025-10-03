"""Client for fetching transactions from the finance API."""
import logging
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class FinanceAPIClient:
    """Client for interacting with the finance API."""
    
    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the Finance API client.
        
        Args:
            base_url: Base URL of the finance API
            username: Username for authentication
            password: Password for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        
        # Authenticate and get token if credentials provided
        if username and password:
            self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authenticate with the finance API and obtain an auth token.
        """
        try:
            url = f"{self.base_url}/api/auth/authenticate"
            logger.info(f"Authenticating with finance API at {url}")
            response = self.session.post(
                url,
                json={"username": self.username, "password": self.password},
                timeout=30
            )
            response.raise_for_status()
            self.token = response.text.removeprefix('"').removesuffix('"')
            
            if self.token:
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                logger.info("Successfully authenticated with finance API")
            else:
                logger.warning("Authentication response did not contain a token")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error authenticating with finance API: {e}")
            raise
    
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
            url = f"{self.base_url}/api/transaction"
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
