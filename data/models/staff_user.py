"""
Staff User module for Vehicle Rental Application.

This module contains the StaffUser class that represents a staff member
in the rental system, extending the abstract Renter class with full
administrative privileges including user management, vehicle management,
and access to analytics.
"""

from renter import Renter
from rental_period import RentalPeriod
from exceptions import InvalidRenterDataError
import re


class StaffUser(Renter):
    """
    Represents a staff member in the vehicle rental system.
    
    This class extends the Renter base class with staff-specific
    attributes and full administrative privileges. Staff users have
    access to all system management functions and do not receive
    rental discounts (they manage the system rather than rent vehicles).
    """
    
    def __init__(self, renter_id: str, name: str, contact_info: str,
                 employee_id: str, role: str, password: str) -> None:
        """
        Initialize a StaffUser object.
        
        Args:
            renter_id (str): Unique identifier for the staff user
            name (str): Full name of the staff member
            contact_info (str): Contact information (phone or email)
            employee_id (str): Employee identification number
            role (str): Staff role (Admin, Manager, Agent)
            password (str): Password for authentication
            
        Raises:
            InvalidRenterDataError: If any staff-specific parameter is invalid
        """
        super().__init__(renter_id, name, contact_info)
        
        self.__employee_id = self._validate_employee_id(employee_id)
        self.__role = self._validate_role(role)
        self.__password = password  # In production, this should be hashed
    
    def _validate_employee_id(self, employee_id: str) -> str:
        """Validate employee ID."""
        if not isinstance(employee_id, str) or not employee_id.strip():
            raise InvalidRenterDataError("employee_id", str(employee_id), "must be a non-empty string")
        
        employee_id = employee_id.strip().upper()
        if len(employee_id) < 3 or len(employee_id) > 20:
            raise InvalidRenterDataError("employee_id", employee_id, "must be 3-20 characters long")
        
        # Check for valid employee ID format (alphanumeric with optional dash)
        if not re.match(r'^[A-Z0-9\-]+$', employee_id):
            raise InvalidRenterDataError("employee_id", employee_id, "invalid format (use letters, numbers, and dashes only)")
        
        return employee_id
    
    def _validate_role(self, role: str) -> str:
        """Validate staff role."""
        if not isinstance(role, str) or not role.strip():
            raise InvalidRenterDataError("role", str(role), "must be a non-empty string")
        
        role = role.strip().title()
        valid_roles = ["Admin", "Manager", "Agent"]
        
        if role not in valid_roles:
            raise InvalidRenterDataError(
                "role", role,
                f"must be one of {', '.join(valid_roles)}"
            )
        
        return role
    
    # Getter methods
    def get_employee_id(self) -> str:
        """Get the employee ID."""
        return self.__employee_id
    
    def get_role(self) -> str:
        """Get the staff role."""
        return self.__role
    
    def get_password(self) -> str:
        """Get the password (for authentication purposes)."""
        return self.__password
    
    # Setter methods
    def set_employee_id(self, employee_id: str) -> None:
        """Set the employee ID."""
        self.__employee_id = self._validate_employee_id(employee_id)
    
    def set_role(self, role: str) -> None:
        """Set the staff role."""
        self.__role = self._validate_role(role)
    
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
    
    def calculate_discount(self, rental_period: RentalPeriod) -> float:
        """
        Calculate the discount percentage for staff users.
        
        Staff users do not receive rental discounts as they are
        system administrators, not regular customers.
        
        Args:
            rental_period (RentalPeriod): The rental period
            
        Returns:
            float: Discount percentage (0.0 for staff)
        """
        # Staff members do not get discounts
        return 0.0
    
    def get_user_type(self) -> str:
        """Get the type of user."""
        return "Staff"
    
    def can_manage_users(self) -> bool:
        """Check if this staff member can manage users."""
        return self.__role in ["Admin", "Manager"]
    
    def can_manage_vehicles(self) -> bool:
        """Check if this staff member can manage vehicles."""
        return self.__role in ["Admin", "Manager"]
    
    def can_view_analytics(self) -> bool:
        """Check if this staff member can view analytics."""
        return self.__role in ["Admin", "Manager"]
    
    def can_process_rentals(self) -> bool:
        """Check if this staff member can process rentals."""
        return True  # All staff can process rentals
    
    def __str__(self) -> str:
        """Return a string representation of the staff user."""
        base_info = super().__str__()
        return f"{base_info}, Employee ID: {self.__employee_id}, Role: {self.__role}"
