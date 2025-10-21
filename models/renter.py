"""
Abstract Renter module for Vehicle Rental Application.

This module contains the abstract Renter class that serves as the base
class for all user types in the rental system, defining common
attributes and methods that all users must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from rental_period import RentalPeriod
from exceptions import InvalidRenterDataError
import re


class Renter(ABC):
    """
    Abstract base class representing a generic renter in the rental system.
    
    This class defines the common interface and shared functionality for all
    user types, ensuring consistent behavior across different user
    implementations while allowing for user-specific discount calculations.
    """
    
    def __init__(self, renter_id: str, name: str, contact_info: str, password: str = "password123") -> None:
        """
        Initialize a Renter object with common attributes.
        
        Args:
            renter_id (str): Unique identifier for the renter
            name (str): Name of the renter
            contact_info (str): Contact information (phone or email)
            password (str): Password for authentication (default: "password123")
            
        Raises:
            InvalidRenterDataError: If any input parameter is invalid
        """
        self.__renter_id = self._validate_renter_id(renter_id)
        self.__name = self._validate_name(name)
        self.__contact_info = self._validate_contact_info(contact_info)
        self.__password = password  # In production, this should be hashed
        
        # Rental management
        self.__current_rentals: List[Dict] = []
        self.__rental_history: List[Dict] = []
    
    def _validate_renter_id(self, renter_id: str) -> str:
        """Validate renter ID."""
        if not isinstance(renter_id, str) or not renter_id.strip():
            raise InvalidRenterDataError("renter_id", str(renter_id), "must be a non-empty string")
        
        renter_id = renter_id.strip()
        if len(renter_id) < 2 or len(renter_id) > 20:
            raise InvalidRenterDataError("renter_id", renter_id, "must be 2-20 characters long")
        
        if not re.match(r'^[A-Za-z0-9_-]+$', renter_id):
            raise InvalidRenterDataError("renter_id", renter_id, "invalid characters")
        
        return renter_id
    
    def _validate_name(self, name: str) -> str:
        """Validate renter name."""
        if not isinstance(name, str):
         raise InvalidRenterDataError("name", str(name), "must be a string")
        name = name.strip()
        if not name:
         raise InvalidRenterDataError("name", name, "cannot be empty")
        if len(name) < 2:
         raise InvalidRenterDataError("name", name, "must be at least 2 characters")
        if len(name) > 100:
         raise InvalidRenterDataError("name", name, "cannot exceed 100 characters")
        if not re.match(r'^[A-Za-z\s\'-\.]+$', name):
         raise InvalidRenterDataError("name", name, "contains invalid characters")
        
        return name
    
    def _validate_contact_info(self, contact_info: str) -> str:
        """Validate contact information (email or phone)."""
        if not isinstance(contact_info, str) or not contact_info.strip():
            raise InvalidRenterDataError("contact_info", str(contact_info), "must be a non-empty string")
        
        contact_info = contact_info.strip()
        
        # Check if it's an email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, contact_info):
            return contact_info
        
        # Check if it's a phone number
        phone_pattern = r'^[\+]?[\d\s\-\(\)]{7,20}$'
        if re.match(phone_pattern, contact_info):
            return contact_info
        
        raise InvalidRenterDataError("contact_info", contact_info, "must be a valid email or phone number")
    
    # Getter methods
    def get_renter_id(self) -> str:
        """Get the renter's unique identifier."""
        return self.__renter_id
    
    def get_name(self) -> str:
        """Get the renter's name."""
        return self.__name
    
    def get_contact_info(self) -> str:
        """Get the renter's contact information."""
        return self.__contact_info
    
    def get_current_rentals(self) -> List[Dict]:
        """Get the list of current active rentals."""
        return self.__current_rentals.copy()
    
    def get_rental_history(self) -> List[Dict]:
        """Get the complete rental history."""
        return self.__rental_history.copy()
    
    def get_password(self) -> str:
        """Get the password (for authentication purposes)."""
        return self.__password
    
    # Setter methods
    def set_renter_id(self, renter_id: str) -> None:
        """Set the renter's unique identifier."""
        self.__renter_id = self._validate_renter_id(renter_id)
    
    def set_name(self, name: str) -> None:
        """Set the renter's name."""
        self.__name = self._validate_name(name)
    
    def set_contact_info(self, contact_info: str) -> None:
        """Set the renter's contact information."""
        self.__contact_info = self._validate_contact_info(contact_info)
    
    def set_password(self, password: str) -> None:
        """Set the password."""
        if not isinstance(password, str) or not password.strip():
            raise InvalidRenterDataError("password", "****", "must be a non-empty string")
        self.__password = password
    
    def verify_password(self, password: str) -> bool:
        """
        Verify if the provided password matches the stored password.
        
        Args:
            password (str): Password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return self.__password == password
    
    # Rental management methods
    def add_rental(self, vehicle_id: str, rental_period: RentalPeriod, rental_cost: float) -> None:
        """Add a new rental to the renter's current rentals."""
        rental_record = {
            'vehicle_id': vehicle_id,
            'start_date': rental_period.get_start_date(),
            'end_date': rental_period.get_end_date(),
            'duration': rental_period.calculate_duration(),
            'cost': rental_cost,
            'status': 'active'
        }
        
        self.__current_rentals.append(rental_record)
        self.__rental_history.append(rental_record.copy())
    
    def complete_rental(self, vehicle_id: str, rental_period: RentalPeriod) -> bool:
        """Complete a rental (move from current to history)."""
        for i, rental in enumerate(self.__current_rentals):
            if (rental['vehicle_id'] == vehicle_id and 
                rental['start_date'] == rental_period.get_start_date() and
                rental['end_date'] == rental_period.get_end_date()):
                
                # Remove from current rentals
                self.__current_rentals.pop(i)
                
                # Update status in history
                for history_rental in self.__rental_history:
                    if (history_rental['vehicle_id'] == vehicle_id and 
                        history_rental['start_date'] == rental_period.get_start_date() and
                        history_rental['end_date'] == rental_period.get_end_date() and
                        history_rental['status'] == 'active'):
                        history_rental['status'] = 'completed'
                        break
                
                return True
        
        return False
    
    def get_total_spent(self) -> float:
        """Calculate total amount spent on rentals."""
        return sum(rental['cost'] for rental in self.__rental_history)
    
    def get_rental_count(self) -> int:
        """Get total number of rentals (including current)."""
        return len(self.__rental_history)
    
    def has_active_rentals(self) -> bool:
        """Check if the renter has any active rentals."""
        return len(self.__current_rentals) > 0
    
    def can_rent_vehicle(self, max_concurrent_rentals: int = 5) -> bool:
        """Check if the renter can rent another vehicle."""
        return len(self.__current_rentals) < max_concurrent_rentals
    
    @abstractmethod
    def calculate_discount(self, rental_period: RentalPeriod) -> float:
        """
        Calculate the discount percentage for a rental period.
        
        This method must be implemented by each user type to provide
        user-specific discount calculations.
        
        Args:
            rental_period (RentalPeriod): The rental period
            
        Returns:
            float: Discount percentage (0.0 to 1.0)
        """
        pass
    
    @abstractmethod
    def get_user_type(self) -> str:
        """
        Get the type of user.
        
        Returns:
            str: Type of user (e.g., "Individual", "Corporate")
        """
        pass
    
    def __str__(self) -> str:
        """Return a string representation of the renter."""
        user_type = self.get_user_type()
        active_rentals = len(self.__current_rentals)
        
        return (f"{user_type} - ID: {self.__renter_id}, Name: {self.__name}, "
                f"Contact: {self.__contact_info}, Active Rentals: {active_rentals}")
    
    def __eq__(self, other) -> bool:
        """Check equality based on renter ID."""
        if not isinstance(other, Renter):
            return False
        return self.__renter_id == other.get_renter_id()
    
    def __hash__(self) -> int:
        """Generate hash based on renter ID."""
        return hash(self.__renter_id)