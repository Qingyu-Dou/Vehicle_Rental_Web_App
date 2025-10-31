"""
Abstract Vehicle module for Vehicle Rental Application.

This module contains the abstract Vehicle class that serves as the base
class for all vehicle types in the rental system, defining common
attributes and methods that all vehicles must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from exceptions import InvalidVehicleDataError, VehicleNotAvailableError
import re


class Vehicle(ABC):
    """
    Abstract base class representing a generic vehicle in the rental system.
    
    This class defines the common interface and shared functionality for all
    vehicle types, ensuring consistent behavior across different vehicle
    implementations while allowing for vehicle-specific customizations.
    """
    
    def __init__(self, vehicle_id: str, make: str, model: str, year: int, daily_rate: float, image_filename: str = 'default.jpg') -> None:
        """
        Initialize a Vehicle object with common attributes.

        Args:
            vehicle_id (str): Unique identifier for the vehicle
            make (str): Manufacturer of the vehicle
            model (str): Model of the vehicle
            year (int): Year the vehicle was manufactured
            daily_rate (float): Daily rental rate for the vehicle
            image_filename (str): Filename of the vehicle image (default: 'default.jpg')

        Raises:
            InvalidVehicleDataError: If any input parameter is invalid
        """
        self.__vehicle_id = self._validate_vehicle_id(vehicle_id)
        self.__make = self._validate_make(make)
        self.__model = self._validate_model(model)
        self.__year = self._validate_year(year)
        self.__daily_rate = self._validate_daily_rate(daily_rate)
        self.__image_filename = self._validate_image_filename(image_filename)

        # Cross-field validation
        self._validate_vehicle_year_vs_rate(self.__year, self.__daily_rate)

        # Rental management - support multiple rentals
        self.__rental_periods: List[Dict[str, Any]] = []
        self.__rental_history: List[Dict[str, Any]] = []
    
    def _validate_vehicle_id(self, vehicle_id: str) -> str:
        """Validate vehicle ID."""
        if not isinstance(vehicle_id, str) or not vehicle_id.strip():
            raise InvalidVehicleDataError("vehicle_id", str(vehicle_id), "must be a non-empty string")
        
        vehicle_id = vehicle_id.strip()
        if len(vehicle_id) < 2 or len(vehicle_id) > 20:
            raise InvalidVehicleDataError("vehicle_id", vehicle_id, "must be 2-20 characters long")
        
        if not re.match(r'^[A-Za-z0-9_-]+$', vehicle_id):
            raise InvalidVehicleDataError("vehicle_id", vehicle_id, "invalid characters")
        
        return vehicle_id
    
    def _validate_make(self, make: str) -> str:
        """Validate vehicle make."""
        if not isinstance(make, str) or not make.strip():
            raise InvalidVehicleDataError("make", str(make), "must be a non-empty string")
        
        make = make.strip()
        if len(make) < 2 or len(make) > 50:
            raise InvalidVehicleDataError("make", make, "must be 2-50 characters long")
        
        return make
    
    def _validate_model(self, model: str) -> str:
        """Validate vehicle model."""
        if not isinstance(model, str) or not model.strip():
            raise InvalidVehicleDataError("model", str(model), "must be a non-empty string")
        
        model = model.strip()
        if len(model) > 50:
            raise InvalidVehicleDataError("model", model, "cannot exceed 50 characters")
        
        return model
    
    def _validate_year(self, year: int) -> int:
        """Validate vehicle year."""
        if not isinstance(year, int):
            raise InvalidVehicleDataError("year", str(year), "must be an integer")
        
        if year < 1990 or year > 2030:
            raise InvalidVehicleDataError("year", str(year), "must be between 1990-2030")
        
        return year
    
    def _validate_daily_rate(self, daily_rate: float) -> float:
        """Validate daily rental rate."""
        if not isinstance(daily_rate, (int, float)):
            raise InvalidVehicleDataError("daily_rate", str(daily_rate), "must be a number")
        
        daily_rate = float(daily_rate)
        if daily_rate <= 0:
            raise InvalidVehicleDataError("daily_rate", str(daily_rate), "must be positive")
        
        return round(daily_rate, 2)
    
    def _validate_vehicle_year_vs_rate(self, year: int, daily_rate: float) -> None:
        """
        Validate the relationship between vehicle year and daily rate.

        Args:
            year (int): Vehicle manufacturing year
            daily_rate (float): Daily rental rate

        Raises:
            InvalidVehicleDataError: If year and rate combination is unrealistic
        """
        from datetime import datetime
        current_year = datetime.now().year

        # Future model vehicles must have higher rates
        if year > current_year and daily_rate < 50:
            raise InvalidVehicleDataError("daily_rate", str(daily_rate),
                                        "future model vehicles must have higher rates (minimum $50)")

        # Very old vehicles shouldn't have premium rates
        if year < 2000 and daily_rate > 200:
            raise InvalidVehicleDataError("daily_rate", str(daily_rate),
                                        "vehicles older than 2000 cannot have premium rates")

        # Luxury rate validation for newer vehicles
        if year >= current_year - 2 and daily_rate > 500:
            raise InvalidVehicleDataError("daily_rate", str(daily_rate),
                                        "daily rate exceeds reasonable limit for new vehicles")

        # Budget validation for older vehicles
        if year < current_year - 10 and daily_rate < 20:
            raise InvalidVehicleDataError("daily_rate", str(daily_rate),
                                        "daily rate too low even for older vehicles")

    def _validate_image_filename(self, image_filename: str) -> str:
        """Validate image filename."""
        if not isinstance(image_filename, str) or not image_filename.strip():
            return 'default.jpg'

        image_filename = image_filename.strip()

        # Check for valid image extensions
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        if not any(image_filename.lower().endswith(ext) for ext in valid_extensions):
            return 'default.jpg'

        return image_filename
    
    # Getter methods
    def get_vehicle_id(self) -> str:
        """Get the vehicle's unique identifier."""
        return self.__vehicle_id
    
    def get_make(self) -> str:
        """Get the vehicle's manufacturer."""
        return self.__make
    
    def get_model(self) -> str:
        """Get the vehicle's model."""
        return self.__model
    
    def get_year(self) -> int:
        """Get the vehicle's manufacturing year."""
        return self.__year
    
    def get_daily_rate(self) -> float:
        """Get the vehicle's daily rental rate."""
        return self.__daily_rate
    
    def get_rental_periods(self) -> List[Dict[str, Any]]:
        """Get all current rental periods for this vehicle."""
        return self.__rental_periods.copy()
    
    def get_rental_history(self) -> List[Dict[str, Any]]:
        """Get the rental history for this vehicle."""
        return self.__rental_history.copy()

    def get_image_filename(self) -> str:
        """Get the vehicle's image filename."""
        # Backward compatibility: return default if attribute doesn't exist
        if not hasattr(self, '_Vehicle__image_filename'):
            return 'default.jpg'
        return self.__image_filename

    # Setter methods
    def set_vehicle_id(self, vehicle_id: str) -> None:
        """Set the vehicle's unique identifier."""
        self.__vehicle_id = self._validate_vehicle_id(vehicle_id)
    
    def set_make(self, make: str) -> None:
        """Set the vehicle's manufacturer."""
        self.__make = self._validate_make(make)
    
    def set_model(self, model: str) -> None:
        """Set the vehicle's model."""
        self.__model = self._validate_model(model)
    
    def set_year(self, year: int) -> None:
        """Set the vehicle's manufacturing year."""
        validated_year = self._validate_year(year)
        # Cross-validate with existing daily rate
        self._validate_vehicle_year_vs_rate(validated_year, self.__daily_rate)
        self.__year = validated_year
    
    def set_daily_rate(self, daily_rate: float) -> None:
        """Set the vehicle's daily rental rate."""
        validated_rate = self._validate_daily_rate(daily_rate)
        # Cross-validate with existing year
        self._validate_vehicle_year_vs_rate(self.__year, validated_rate)
        self.__daily_rate = validated_rate

    def set_image_filename(self, image_filename: str) -> None:
        """Set the vehicle's image filename."""
        # Use name mangling to set the attribute
        self._Vehicle__image_filename = self._validate_image_filename(image_filename)

    # Rental management methods
    def is_available(self, rental_period) -> bool:
        """
        Check if the vehicle is available for the given rental period.
        Considers both active and completed rentals (using actual return dates).
        """
        # Check if object has required methods instead of isinstance (to avoid import issues)
        if not (hasattr(rental_period, 'get_start_date') and
                hasattr(rental_period, 'get_end_date') and
                hasattr(rental_period, 'overlaps_with')):
            raise TypeError("rental_period must be a RentalPeriod object with required methods")

        # Check against all existing rental periods using overlaps_with method
        from rental_period import RentalPeriod
        for existing_period_dict in self.__rental_periods:
            try:
                # For completed rentals, use actual_end_date if available
                # For active rentals, use scheduled end_date
                if existing_period_dict.get('status') == 'completed' and 'actual_end_date' in existing_period_dict:
                    end_date = existing_period_dict['actual_end_date']
                else:
                    end_date = existing_period_dict['end_date']

                existing_period = RentalPeriod(
                    existing_period_dict['start_date'],
                    end_date,
                    allow_past_dates=True  # Allow past dates when checking existing periods
                )
                if rental_period.overlaps_with(existing_period):
                    return False
            except Exception:
                continue

        return True
    
    def add_rental(self, rental_period, renter_id: str) -> None:
        """Add a new rental period for this vehicle."""
        if not self.is_available(rental_period):
            raise VehicleNotAvailableError(
                self.__vehicle_id,
                rental_period.get_start_date(),
                rental_period.get_end_date()
            )
        
        rental_dict = {
            'start_date': rental_period.get_start_date(),
            'end_date': rental_period.get_end_date(),
            'duration': rental_period.calculate_duration(),
            'renter_id': renter_id,
            'status': 'active'
        }
        
        self.__rental_periods.append(rental_dict)
        self.__rental_history.append(rental_dict.copy())
    
    def remove_rental(self, rental_period, actual_return_date: str = None) -> bool:
        """
        Mark a rental period as completed when vehicle is returned.
        The rental record remains to block those dates from future bookings.

        Args:
            rental_period: The original scheduled rental period
            actual_return_date: The actual return date (DD-MM-YYYY), if different from scheduled
        """
        for period_dict in self.__rental_periods:
            if (period_dict['start_date'] == rental_period.get_start_date() and
                period_dict['end_date'] == rental_period.get_end_date() and
                period_dict['status'] == 'active'):

                # Mark as completed instead of removing
                period_dict['status'] = 'completed'

                # Update with actual return date if provided
                if actual_return_date:
                    period_dict['actual_end_date'] = actual_return_date
                else:
                    period_dict['actual_end_date'] = rental_period.get_end_date()

                # Update rental history
                for record in self.__rental_history:
                    if (record['start_date'] == rental_period.get_start_date() and
                        record['end_date'] == rental_period.get_end_date() and
                        record['status'] == 'active'):
                        record['status'] = 'completed'
                        if actual_return_date:
                            record['actual_end_date'] = actual_return_date
                        else:
                            record['actual_end_date'] = rental_period.get_end_date()
                        break
                return True
        return False

    def restore_active_rental(self, rental_period) -> bool:
        """
        Restore a rental to active status (used for rollback when return fails).

        Args:
            rental_period: The rental period to restore
        """
        for period_dict in self.__rental_periods:
            if (period_dict['start_date'] == rental_period.get_start_date() and
                period_dict['end_date'] == rental_period.get_end_date() and
                period_dict['status'] == 'completed'):

                # Restore to active status
                period_dict['status'] = 'active'
                if 'actual_end_date' in period_dict:
                    del period_dict['actual_end_date']

                # Update rental history
                for record in self.__rental_history:
                    if (record['start_date'] == rental_period.get_start_date() and
                        record['end_date'] == rental_period.get_end_date() and
                        record['status'] == 'completed'):
                        record['status'] = 'active'
                        if 'actual_end_date' in record:
                            del record['actual_end_date']
                        break
                return True
        return False

    def is_currently_rented(self) -> bool:
        """Check if the vehicle is currently rented (has active rentals)."""
        return any(period['status'] == 'active' for period in self.__rental_periods)
    
    def get_base_rental_cost(self, rental_period) -> float:
        """Calculate base rental cost without discounts."""
        duration = rental_period.calculate_duration()
        return round(duration * self.__daily_rate, 2)
    
    def apply_discount(self, base_cost: float, discount_percentage: float) -> float:
        """Apply discount to base cost."""
        if not 0.0 <= discount_percentage <= 1.0:
            discount_percentage = max(0.0, min(1.0, discount_percentage))
        
        discount_amount = base_cost * discount_percentage
        final_cost = base_cost - discount_amount
        return round(final_cost, 2)
    
    @abstractmethod
    def calculate_rental_cost(self, rental_period, user_discount: float = 0.0) -> float:
        """Calculate the rental cost for a given period with discount."""
        pass
    
    @abstractmethod
    def get_vehicle_type(self) -> str:
        """Get the type of vehicle."""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """Return a string representation of the vehicle."""
        pass
    
    def __eq__(self, other) -> bool:
        """Check equality based on vehicle ID."""
        if not isinstance(other, Vehicle):
            return False
        return self.__vehicle_id == other.get_vehicle_id()
    
    def __hash__(self) -> int:
        """Generate hash based on vehicle ID."""
        return hash(self.__vehicle_id)