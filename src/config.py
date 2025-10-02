"""Configuration module for transaction importer."""
import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the transaction importer."""
    
    # Finance API Configuration
    FINANCE_API_URL: str = os.getenv("FINANCE_API_URL", "http://localhost:5000")
    FINANCE_API_USERNAME: Optional[str] = os.getenv("FINANCE_API_USERNAME")
    FINANCE_API_PASSWORD: Optional[str] = os.getenv("FINANCE_API_PASSWORD")
    
    # Actual Budget Configuration
    ACTUAL_SERVER_URL: str = os.getenv("ACTUAL_SERVER_URL", "http://localhost:5006")
    ACTUAL_PASSWORD: Optional[str] = os.getenv("ACTUAL_PASSWORD")
    ACTUAL_BUDGET_ID: Optional[str] = os.getenv("ACTUAL_BUDGET_ID")
    ACTUAL_ENCRYPTION_KEY: Optional[str] = os.getenv("ACTUAL_ENCRYPTION_KEY")
    
    # Account Mapping Configuration
    _ACCOUNT_MAPPING_STR: Optional[str] = os.getenv("ACCOUNT_MAPPING", "")
    
    @classmethod
    def get_account_mapping(cls) -> Dict[str, str]:
        """Parse and return account mapping dictionary."""
        if not cls._ACCOUNT_MAPPING_STR:
            return {}
        
        mapping = {}
        for pair in cls._ACCOUNT_MAPPING_STR.split(","):
            if ":" in pair:
                finance_id, actual_id = pair.split(":", 1)
                mapping[finance_id.strip()] = actual_id.strip()
        return mapping
    
    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present."""
        errors = []
        
        if not cls.FINANCE_API_URL:
            errors.append("FINANCE_API_URL is required")
        
        if not cls.ACTUAL_SERVER_URL:
            errors.append("ACTUAL_SERVER_URL is required")
        
        if not cls.ACTUAL_PASSWORD:
            errors.append("ACTUAL_PASSWORD is required")
        
        if not cls.ACTUAL_BUDGET_ID:
            errors.append("ACTUAL_BUDGET_ID is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
