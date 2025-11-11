"""Amount generators for GL transactions."""
import random
from core.models import Account


class AmountGenerator:
    """Generates realistic transaction amounts based on account type."""
    
    REVENUE_MIN = 5000.0
    REVENUE_MAX = 50000.0
    
    CAPEX_MIN = 10000.0
    CAPEX_MAX = 200000.0
    
    OPEX_MIN = 500.0
    OPEX_MAX = 15000.0
    
    def generate_for_account(self, account: Account) -> tuple[float, float]:
        """
        Generate debit and credit amounts for an account.
        
        Returns:
            Tuple of (debit_amount, credit_amount)
        """
        if account.is_revenue():
            base_amount = random.uniform(self.REVENUE_MIN, self.REVENUE_MAX)
            return (0.0, round(base_amount, 2))
        elif account.is_capex():
            base_amount = random.uniform(self.CAPEX_MIN, self.CAPEX_MAX)
            return (round(base_amount, 2), 0.0)
        else:  # Operating/Admin expenses
            base_amount = random.uniform(self.OPEX_MIN, self.OPEX_MAX)
            return (round(base_amount, 2), 0.0)

