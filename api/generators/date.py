"""Date generators for GL transactions."""
import random
from datetime import datetime, timedelta


class DateGenerator:
    """Generates transaction dates."""
    
    def generate_transaction_date(self, historical_probability: float = 0.8) -> datetime.date:
        """
        Generate transaction date, sometimes historical for realism.
        
        Args:
            historical_probability: Probability of generating a historical date (default 0.8)
        """
        if random.random() < historical_probability:
            days_ago = random.randint(0, 30)
            return (datetime.now() - timedelta(days=days_ago)).date()
        return datetime.now().date()
    
    def get_posting_date(self) -> datetime.date:
        """Get current posting date."""
        return datetime.now().date()

