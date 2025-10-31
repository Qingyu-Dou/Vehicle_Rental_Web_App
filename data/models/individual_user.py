"""
Individual User module for Vehicle Rental Application.

This module contains the IndividualUser class that represents an individual
customer in the rental system, extending the abstract Renter class with
individual-specific discount calculations and attributes.
"""

from renter import Renter
from rental_period import RentalPeriod
from exceptions import InvalidRenterDataError
from datetime import datetime
import re


class IndividualUser(Renter):
    """
    Represents an individual customer in the vehicle rental system.
    
    This class extends the Renter base class with individual-specific
    discount calculations, where discounts are applied only for rental
    periods of 7 or more days.
    """
    
    def __init__(self, renter_id: str, name: str, contact_info: str, 
                 date_of_birth: str, license_number: str, password: str = "password123") -> None:
        """
        Initialize an IndividualUser object.
        
        Args:
            renter_id (str): Unique identifier for the individual user
            name (str): Full name of the individual
            contact_info (str): Contact information (phone or email)
            date_of_birth (str): Date of birth in DD-MM-YYYY format
            license_number (str): Driver's license number
            password (str): Password for authentication (default: "password123")
            
        Raises:
            InvalidRenterDataError: If any individual-specific parameter is invalid
        """
        super().__init__(renter_id, name, contact_info, password)
        
        self.__date_of_birth = self._validate_date_of_birth(date_of_birth)
        self.__license_number = self._validate_license_number(license_number)
    
    def _validate_date_of_birth(self, date_of_birth: str) -> str:
        """Validate date of birth."""
        if not isinstance(date_of_birth, str) or not date_of_birth.strip():
            raise InvalidRenterDataError("date_of_birth", str(date_of_birth), "must be a non-empty string")
        
        date_of_birth = date_of_birth.strip()
        
        # Basic format validation (DD-MM-YYYY)
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', date_of_birth):
            raise InvalidRenterDataError("date_of_birth", date_of_birth, "must be in DD-MM-YYYY format")
        
        # Parse and validate date
        try:
            birth_date = datetime.strptime(date_of_birth, "%d-%m-%Y")
            current_date = datetime.now()
            
            # Check if birth date is in the future
            if birth_date > current_date:
                raise InvalidRenterDataError("date_of_birth", date_of_birth, "cannot be in the future")
            
            # Check if person is at least 18 years old
            age = (current_date - birth_date).days / 365.25
            if age < 18:
                raise InvalidRenterDataError("date_of_birth", date_of_birth, "user must be at least 18 years old")
            
            # Check if person is not unreasonably old (over 120)
            if age > 120:
                raise InvalidRenterDataError("date_of_birth", date_of_birth, "invalid birth date")
                
        except ValueError:
            raise InvalidRenterDataError("date_of_birth", date_of_birth, "invalid date format")
        
        return date_of_birth
    
    def _validate_license_number(self, license_number: str) -> str:
        """Validate driver's license number."""
        if not isinstance(license_number, str) or not license_number.strip():
            raise InvalidRenterDataError("license_number", str(license_number), "must be a non-empty string")
        
        license_number = license_number.strip().upper()
        
        if len(license_number) < 5 or len(license_number) > 20:
            raise InvalidRenterDataError("license_number", license_number, "must be 5-20 characters long")
        
        # Check for valid license format (alphanumeric)
        if not re.match(r'^[A-Z0-9]+$', license_number):
            raise InvalidRenterDataError("license_number", license_number, "can only contain letters and numbers")
        
        return license_number
    
    # Getter methods
    def get_date_of_birth(self) -> str:
        """Get the date of birth."""
        return self.__date_of_birth
    
    def get_license_number(self) -> str:
        """Get the driver's license number."""
        return self.__license_number
    
    # Setter methods
    def set_date_of_birth(self, date_of_birth: str) -> None:
        """Set the date of birth."""
        self.__date_of_birth = self._validate_date_of_birth(date_of_birth)
    
    def set_license_number(self, license_number: str) -> None:
        """Set the driver's license number."""
        self.__license_number = self._validate_license_number(license_number)
    
    def calculate_discount(self, rental_period: RentalPeriod) -> float:
        """
        Calculate the discount percentage for individual users.
        
        Individual users get discount only for rental periods of 7 or more days.
        
        Args:
            rental_period (RentalPeriod): The rental period
            
        Returns:
            float: Discount percentage (0.0 to 0.1)
        """
        # Check for required method instead of isinstance to avoid import issues
        if not hasattr(rental_period, 'calculate_duration'):
            raise TypeError("rental_period must have calculate_duration method")
        
        duration = rental_period.calculate_duration()
        
        # Discount only for 7+ days
        if duration >= 7:
            return 0.10  # 10% discount for 7+ days
        else:
            return 0.0   # No discount for short-term rentals
    
    def get_user_type(self) -> str:
        """Get the type of user."""
        return "Individual"
    
    def __str__(self) -> str:
        """Return a string representation of the individual user."""
        base_info = super().__str__()
        return f"{base_info}, License: {self.__license_number}"