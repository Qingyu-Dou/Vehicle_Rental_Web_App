"""
Motorbike module for Vehicle Rental Application.

This module contains the Motorbike class that represents a motorbike in the rental system,
extending the abstract Vehicle class with motorbike-specific attributes and methods.
"""

from vehicle import Vehicle
from rental_period import RentalPeriod
from exceptions import InvalidVehicleDataError


class Motorbike(Vehicle):
    """
    Represents a motorbike in the vehicle rental system.
    
    This class extends the Vehicle base class with motorbike-specific attributes
    such as engine capacity, bike type, and safety features, and implements
    motorbike-specific rental cost calculations.
    """
    
    def __init__(self, vehicle_id: str, make: str, model: str, year: int, daily_rate: float,
                 engine_capacity: int, bike_type: str, has_abs: bool) -> None:
        """
        Initialize a Motorbike object.
        
        Args:
            vehicle_id (str): Unique identifier for the motorbike
            make (str): Manufacturer of the motorbike
            model (str): Model of the motorbike
            year (int): Year the motorbike was manufactured
            daily_rate (float): Daily rental rate for the motorbike
            engine_capacity (int): Engine capacity in CC
            bike_type (str): Type of bike (Sport, Cruiser, Touring, Adventure, Standard)
            has_abs (bool): Whether the bike has ABS braking system
            
        Raises:
            InvalidVehicleDataError: If any motorbike-specific parameter is invalid
        """
        super().__init__(vehicle_id, make, model, year, daily_rate)
        
        self.__engine_capacity = self._validate_engine_capacity(engine_capacity)
        self.__bike_type = self._validate_bike_type(bike_type)
        self.__has_abs = self._validate_has_abs(has_abs)
    
    def _validate_engine_capacity(self, engine_capacity: int) -> int:
        """Validate engine capacity."""
        if not isinstance(engine_capacity, int):
            raise InvalidVehicleDataError("engine_capacity", str(engine_capacity), "must be an integer")
        
        if engine_capacity < 50 or engine_capacity > 2000:
            raise InvalidVehicleDataError("engine_capacity", str(engine_capacity), "must be between 50-2000cc")
        
        return engine_capacity
    
    def _validate_bike_type(self, bike_type: str) -> str:
        """Validate bike type."""
        if not isinstance(bike_type, str):
            raise InvalidVehicleDataError("bike_type", str(bike_type), "must be a string")
        
        bike_type = bike_type.strip().title()
        valid_bike_types = ["Sport", "Cruiser", "Touring", "Adventure", "Standard"]
        
        if bike_type not in valid_bike_types:
            raise InvalidVehicleDataError(
                "bike_type", bike_type,
                f"must be one of {', '.join(valid_bike_types)}"
            )
        
        return bike_type
    
    def _validate_has_abs(self, has_abs: bool) -> bool:
        """Validate ABS flag."""
        if not isinstance(has_abs, bool):
            raise InvalidVehicleDataError("has_abs", str(has_abs), "must be a boolean")
        
        return has_abs
    
    # Getter methods
    def get_engine_capacity(self) -> int:
        """Get the engine capacity in CC."""
        return self.__engine_capacity
    
    def get_bike_type(self) -> str:
        """Get the bike type."""
        return self.__bike_type
    
    def has_abs_braking(self) -> bool:
        """Check if the bike has ABS braking system."""
        return self.__has_abs
    
    # Setter methods
    def set_engine_capacity(self, engine_capacity: int) -> None:
        """Set the engine capacity."""
        self.__engine_capacity = self._validate_engine_capacity(engine_capacity)
    
    def set_bike_type(self, bike_type: str) -> None:
        """Set the bike type."""
        self.__bike_type = self._validate_bike_type(bike_type)
    
    def set_has_abs(self, has_abs: bool) -> None:
        """Set the ABS flag."""
        self.__has_abs = self._validate_has_abs(has_abs)
    
    def calculate_rental_cost(self, rental_period: RentalPeriod, user_discount: float = 0.0) -> float:
        """
        Calculate the rental cost for a motorbike with bike-specific adjustments.
        
        Args:
            rental_period (RentalPeriod): The rental period
            user_discount (float): User-specific discount percentage (0.0 to 1.0)
            
        Returns:
            float: Total rental cost after discounts and adjustments
        """
        base_cost = self.get_base_rental_cost(rental_period)
        
        # Motorbike-specific pricing adjustments
        premium_multiplier = 1.0
        
        # Engine capacity adjustments
        if self.__engine_capacity >= 1000:
            premium_multiplier += 0.25  # Large bikes premium
        elif self.__engine_capacity >= 600:
            premium_multiplier += 0.15  # Medium bikes premium
        elif self.__engine_capacity >= 300:
            premium_multiplier += 0.05  # Small premium for moderate bikes
        
        # Bike type adjustments
        if self.__bike_type == "Sport":
            premium_multiplier += 0.20
        elif self.__bike_type == "Adventure":
            premium_multiplier += 0.15
        elif self.__bike_type == "Touring":
            premium_multiplier += 0.10
        
        # ABS safety premium
        if self.__has_abs:
            premium_multiplier += 0.05
        
        adjusted_cost = base_cost * premium_multiplier
        final_cost = self.apply_discount(adjusted_cost, user_discount)
        
        return round(final_cost, 2)
    
    def get_vehicle_type(self) -> str:
        """Get the type of vehicle."""
        return "Motorbike"
    
    def __str__(self) -> str:
        """Return a string representation of the motorbike."""
        availability_status = "Available" if not self.is_currently_rented() else "Rented"
        abs_info = "with ABS" if self.__has_abs else "without ABS"
        
        return (f"Motorbike ID: {self.get_vehicle_id()}, {self.get_year()} {self.get_make()} {self.get_model()}, "
                f"Daily Rate: ${self.get_daily_rate():.2f}, {self.__engine_capacity}cc {self.__bike_type} "
                f"({abs_info}), Status: {availability_status}")