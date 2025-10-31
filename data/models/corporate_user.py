"""
Corporate User module for Vehicle Rental Application.

This module contains the CorporateUser class that represents a corporate
customer in the rental system, extending the abstract Renter class with
corporate-specific discount calculations and attributes.
"""

from renter import Renter
from rental_period import RentalPeriod
from exceptions import InvalidRenterDataError
import re


class CorporateUser(Renter):
    """
    Represents a corporate customer in the vehicle rental system.
    
    This class extends the Renter base class with corporate-specific
    discount calculations, where corporate users receive a 15%
    discount on all rentals regardless of rental period.
    """
    
    def __init__(self, renter_id: str, name: str, contact_info: str,
                 company_name: str, business_registration: str, billing_address: str,
                 password: str = "password123") -> None:
        """
        Initialize a CorporateUser object.
        
        Args:
            renter_id (str): Unique identifier for the corporate user
            name (str): Name of the primary contact person
            contact_info (str): Contact information (phone or email)
            company_name (str): Official name of the company
            business_registration (str): Business registration number
            billing_address (str): Company billing address
            password (str): Password for authentication (default: "password123")
            
        Raises:
            InvalidRenterDataError: If any corporate-specific parameter is invalid
        """
        super().__init__(renter_id, name, contact_info, password)
        
        self.__company_name = self._validate_company_name(company_name)
        self.__business_registration = self._validate_business_registration(business_registration)
        self.__billing_address = self._validate_billing_address(billing_address)
    
    def _validate_company_name(self, company_name: str) -> str:
        """Validate company name."""
        if not isinstance(company_name, str) or not company_name.strip():
            raise InvalidRenterDataError("company_name", str(company_name), "must be a non-empty string")
        
        company_name = company_name.strip()
        if len(company_name) < 2 or len(company_name) > 200:
            raise InvalidRenterDataError("company_name", company_name, "must be 2-200 characters long")
        
        # Check for valid company name characters
        if not re.match(r'^[A-Za-z0-9\s\'-\.\&\(\),]+$', company_name):
            raise InvalidRenterDataError("company_name", company_name, "contains invalid characters")
        
        return company_name
    
    def _validate_business_registration(self, business_registration: str) -> str:
        """Validate business registration number."""
        if not isinstance(business_registration, str) or not business_registration.strip():
            raise InvalidRenterDataError("business_registration", str(business_registration), "must be a non-empty string")
        
        business_registration = business_registration.strip().upper()
        if len(business_registration) < 5 or len(business_registration) > 30:
            raise InvalidRenterDataError("business_registration", business_registration, "must be 5-30 characters long")
        
        # Check for valid registration format (alphanumeric with some special chars)
        if not re.match(r'^[A-Z0-9\-\/]+$', business_registration):
            raise InvalidRenterDataError("business_registration", business_registration, "invalid format")
        
        return business_registration
    
    def _validate_billing_address(self, billing_address: str) -> str:
        """Validate billing address."""
        if not isinstance(billing_address, str) or not billing_address.strip():
            raise InvalidRenterDataError("billing_address", str(billing_address), "must be a non-empty string")
        
        billing_address = billing_address.strip()
        if len(billing_address) < 10 or len(billing_address) > 500:
            raise InvalidRenterDataError("billing_address", billing_address, "must be 10-500 characters long")
        
        return billing_address
    
    # Getter methods
    def get_company_name(self) -> str:
        """Get the company name."""
        return self.__company_name
    
    def get_business_registration(self) -> str:
        """Get the business registration number."""
        return self.__business_registration
    
    def get_billing_address(self) -> str:
        """Get the billing address."""
        return self.__billing_address
    
    # Setter methods
    def set_company_name(self, company_name: str) -> None:
        """Set the company name."""
        self.__company_name = self._validate_company_name(company_name)
    
    def set_business_registration(self, business_registration: str) -> None:
        """Set the business registration number."""
        self.__business_registration = self._validate_business_registration(business_registration)
    
    def set_billing_address(self, billing_address: str) -> None:
        """Set the billing address."""
        self.__billing_address = self._validate_billing_address(billing_address)
    
    def calculate_discount(self, rental_period: RentalPeriod) -> float:
        """
        Calculate the discount percentage for corporate users.
        
        Corporate users receive a 15% discount on all rentals,
        regardless of the rental period duration.
        
        Args:
            rental_period (RentalPeriod): The rental period
            
        Returns:
            float: Discount percentage (0.15)
        """
        # Corporate users always get 15% discount (no need to check rental_period details)
        # 15% corporate discount
        return 0.15
    
    def get_user_type(self) -> str:
        """Get the type of user."""
        return "Corporate"
    
    def __str__(self) -> str:
        """Return a string representation of the corporate user."""
        base_info = super().__str__()
        return f"{base_info}, Company: {self.__company_name}"