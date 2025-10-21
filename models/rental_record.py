"""
Rental Record module for Vehicle Rental Application.

This module contains the RentalRecord class that represents a complete
rental transaction, linking a vehicle, renter, rental period, and cost
information together for better tracking and management.
"""

from datetime import datetime
from typing import Optional


class RentalRecord:
    """
    Represents a complete rental transaction record.
    
    This class encapsulates all information about a rental transaction,
    including the vehicle rented, the renter, the rental period, cost,
    and status. It provides a centralized way to manage rental information.
    """
    
    # Valid rental statuses
    VALID_STATUSES = ['pending', 'active', 'completed', 'cancelled', 'overdue']
    
    def __init__(self, record_id: str, vehicle_id: str, renter_id: str,
                 start_date: str, end_date: str, rental_cost: float,
                 status: str = 'pending', discount_applied: float = 0.0) -> None:
        """
        Initialize a RentalRecord object.
        
        Args:
            record_id (str): Unique identifier for this rental record
            vehicle_id (str): ID of the rented vehicle
            renter_id (str): ID of the renter
            start_date (str): Rental start date (DD-MM-YYYY format)
            end_date (str): Rental end date (DD-MM-YYYY format)
            rental_cost (float): Total rental cost after discounts
            status (str): Rental status (pending, active, completed, cancelled, overdue)
            discount_applied (float): Discount percentage applied (0.0 to 1.0)
        """
        self.__record_id = record_id
        self.__vehicle_id = vehicle_id
        self.__renter_id = renter_id
        self.__start_date = start_date
        self.__end_date = end_date
        self.__rental_cost = rental_cost
        self.__status = self._validate_status(status)
        self.__discount_applied = discount_applied
        self.__created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__updated_at = self.__created_at
    
    def _validate_status(self, status: str) -> str:
        """Validate rental status."""
        status = status.lower().strip()
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}. Must be one of {', '.join(self.VALID_STATUSES)}")
        return status
    
    # Getter methods
    def get_record_id(self) -> str:
        """Get the rental record ID."""
        return self.__record_id
    
    def get_vehicle_id(self) -> str:
        """Get the vehicle ID."""
        return self.__vehicle_id
    
    def get_renter_id(self) -> str:
        """Get the renter ID."""
        return self.__renter_id
    
    def get_start_date(self) -> str:
        """Get the rental start date."""
        return self.__start_date
    
    def get_end_date(self) -> str:
        """Get the rental end date."""
        return self.__end_date
    
    def get_rental_cost(self) -> float:
        """Get the rental cost."""
        return self.__rental_cost
    
    def get_status(self) -> str:
        """Get the rental status."""
        return self.__status
    
    def get_discount_applied(self) -> float:
        """Get the discount percentage applied."""
        return self.__discount_applied
    
    def get_created_at(self) -> str:
        """Get the record creation timestamp."""
        return self.__created_at
    
    def get_updated_at(self) -> str:
        """Get the last update timestamp."""
        return self.__updated_at
    
    # Setter methods
    def set_status(self, status: str) -> None:
        """Update the rental status."""
        self.__status = self._validate_status(status)
        self.__updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def set_rental_cost(self, rental_cost: float) -> None:
        """Update the rental cost."""
        if rental_cost < 0:
            raise ValueError("Rental cost cannot be negative")
        self.__rental_cost = round(rental_cost, 2)
        self.__updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Status check methods
    def is_active(self) -> bool:
        """Check if the rental is currently active."""
        return self.__status == 'active'
    
    def is_completed(self) -> bool:
        """Check if the rental is completed."""
        return self.__status == 'completed'
    
    def is_overdue(self) -> bool:
        """Check if the rental is overdue."""
        return self.__status == 'overdue'
    
    def is_pending(self) -> bool:
        """Check if the rental is pending."""
        return self.__status == 'pending'
    
    # Status update methods
    def mark_as_active(self) -> None:
        """Mark the rental as active."""
        self.set_status('active')
    
    def mark_as_completed(self) -> None:
        """Mark the rental as completed."""
        self.set_status('completed')
    
    def mark_as_overdue(self) -> None:
        """Mark the rental as overdue."""
        self.set_status('overdue')
    
    def mark_as_cancelled(self) -> None:
        """Mark the rental as cancelled."""
        self.set_status('cancelled')
    
    def calculate_duration(self) -> int:
        """
        Calculate the rental duration in days.
        
        Returns:
            int: Number of days in the rental period
        """
        try:
            start = datetime.strptime(self.__start_date, "%d-%m-%Y")
            end = datetime.strptime(self.__end_date, "%d-%m-%Y")
            return (end - start).days + 1
        except ValueError:
            return 0
    
    def check_if_overdue(self) -> bool:
        """
        Check if the rental should be marked as overdue based on current date.
        
        Returns:
            bool: True if rental is past end date and still active, False otherwise
        """
        if self.__status != 'active':
            return False
        
        try:
            end_date = datetime.strptime(self.__end_date, "%d-%m-%Y")
            current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if current_date > end_date:
                self.mark_as_overdue()
                return True
        except ValueError:
            pass
        
        return False
    
    def to_dict(self) -> dict:
        """
        Convert rental record to dictionary format.
        
        Returns:
            dict: Dictionary representation of the rental record
        """
        return {
            'record_id': self.__record_id,
            'vehicle_id': self.__vehicle_id,
            'renter_id': self.__renter_id,
            'start_date': self.__start_date,
            'end_date': self.__end_date,
            'rental_cost': self.__rental_cost,
            'status': self.__status,
            'discount_applied': self.__discount_applied,
            'duration': self.calculate_duration(),
            'created_at': self.__created_at,
            'updated_at': self.__updated_at
        }
    
    def __str__(self) -> str:
        """Return a string representation of the rental record."""
        duration = self.calculate_duration()
        return (f"Rental Record {self.__record_id}: Vehicle {self.__vehicle_id} rented by "
                f"{self.__renter_id} from {self.__start_date} to {self.__end_date} "
                f"({duration} days) - Cost: ${self.__rental_cost:.2f} - Status: {self.__status.upper()}")
    
    def __eq__(self, other) -> bool:
        """Check equality based on record ID."""
        if not isinstance(other, RentalRecord):
            return False
        return self.__record_id == other.get_record_id()
    
    def __hash__(self) -> int:
        """Generate hash based on record ID."""
        return hash(self.__record_id)
