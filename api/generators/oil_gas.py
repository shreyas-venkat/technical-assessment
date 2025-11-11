"""Oil & gas specific data generators."""
import random
from datetime import datetime, date


class OilGasDataGenerator:
    """Generates oil & gas specific identifiers."""
    
    BASINS = ["Permian", "Eagle Ford", "Bakken", "Marcellus", "Haynesville", "Utica", "Anadarko", "DJ Basin"]
    STATES = ["TX", "ND", "PA", "LA", "OK", "CO", "WY", "NM"]
    COUNTIES = ["Midland", "Reeves", "Ward", "Loving", "Karnes", "DeWitt", "Mountrail", "Williams"]
    
    def generate_well_id(self) -> str:
        """Generate realistic well ID format: BASIN-WELLNUMBER."""
        basin = random.choice(self.BASINS)
        well_num = random.randint(1000, 9999)
        return f"{basin.upper()[:4]}-{well_num}"
    
    def generate_afe_number(self) -> str:
        """Generate AFE (Authorization for Expenditure) number."""
        return f"AFE-{random.randint(2020, 2024)}-{random.randint(1000, 9999)}"
    
    def generate_lease_name(self) -> str:
        """Generate lease/property name."""
        prefixes = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        suffixes = ["Ranch", "Field", "Unit", "Lease", "Property", "Tract"]
        return f"{random.choice(prefixes)} {random.choice(suffixes)}"
    
    def generate_property_id(self) -> str:
        """Generate property/lease ID."""
        return f"PROP-{random.choice(self.STATES)}-{random.randint(10000, 99999)}"
    
    def generate_jib_number(self, transaction_date: date = None) -> str:
        """Generate Joint Interest Billing number."""
        if transaction_date:
            date_str = transaction_date.strftime('%Y%m')
        else:
            date_str = datetime.now().strftime('%Y%m')
        return f"JIB-{random.choice(self.STATES)}-{random.randint(1000, 9999)}-{date_str}"
    
    def generate_cost_center(self) -> str:
        """Generate cost center code."""
        return f"CC-{random.choice(['NORTH', 'SOUTH', 'EAST', 'WEST', 'CENTRAL'])}-{random.randint(1, 9)}"
    
    def generate_basin(self) -> str:
        """Generate a random basin."""
        return random.choice(self.BASINS)
    
    def generate_state(self) -> str:
        """Generate a random state."""
        return random.choice(self.STATES)
    
    def generate_county(self) -> str:
        """Generate a random county."""
        return random.choice(self.COUNTIES)

