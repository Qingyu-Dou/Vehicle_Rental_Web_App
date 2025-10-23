"""
Truck module for Vehicle Rental Application.

This module contains the Truck class that represents a truck in the rental system,
extending the abstract Vehicle class with truck-specific attributes and methods.
"""

from vehicle import Vehicle
from rental_period import RentalPeriod
from exceptions import InvalidVehicleDataError


class Truck(Vehicle):
    """
    Represents a truck in the vehicle rental system.
    
    This class extends the Vehicle base class with truck-specific attributes
    such as load capacity, truck type, and cargo features, and implements
    truck-specific rental cost calculations.
    """
    
    def __init__(self, vehicle_id: str, make: str, model: str, year: int, daily_rate: float,
                 load_capacity: float, truck_type: str, has_hydraulic_lift: bool) -> None:
        """
        Initialize a Truck object.

        Args:
            vehicle_id (str): Unique identifier for the truck
            make (str): Manufacturer of the truck
            model (str): Model of the truck
            year (int): Year the truck was manufactured
            daily_rate (float): Daily rental rate for the truck
            load_capacity (float): Load capacity in tonnes
            truck_type (str): Type of truck (Light, Medium, Heavy, Box, Flatbed)
            has_hydraulic_lift (bool): Whether the truck has hydraulic lift system

        Raises:
            InvalidVehicleDataError: If any truck-specific parameter is invalid
        """
        super().__init__(vehicle_id, make, model, year, daily_rate)
        
        self.__load_capacity = self._validate_load_capacity(load_capacity)
        self.__truck_type = self._validate_truck_type(truck_type)
        self.__has_hydraulic_lift = self._validate_has_hydraulic_lift(has_hydraulic_lift)
    
    def _validate_load_capacity(self, load_capacity: float) -> float:
        """Validate load capacity."""
        if not isinstance(load_capacity, (int, float)):
            raise InvalidVehicleDataError("load_capacity", str(load_capacity), "must be a number")
        
        load_capacity = float(load_capacity)
        
        if load_capacity <= 0 or load_capacity > 50:
            raise InvalidVehicleDataError("load_capacity", str(load_capacity), "must be between 0-50 tonnes")
        
        return round(load_capacity, 2)
    
    def _validate_truck_type(self, truck_type: str) -> str:
        """Validate truck type."""
        if not isinstance(truck_type, str):
            raise InvalidVehicleDataError("truck_type", str(truck_type), "must be a string")
        
        truck_type = truck_type.strip().title()
        valid_truck_types = ["Light", "Medium", "Heavy", "Box", "Flatbed"]
        
        if truck_type not in valid_truck_types:
            raise InvalidVehicleDataError(
                "truck_type", truck_type,
                f"must be one of {', '.join(valid_truck_types)}"
            )
        
        return truck_type
    
    def _validate_has_hydraulic_lift(self, has_hydraulic_lift: bool) -> bool:
        """Validate hydraulic lift flag."""
        if not isinstance(has_hydraulic_lift, bool):
            raise InvalidVehicleDataError("has_hydraulic_lift", str(has_hydraulic_lift), "must be a boolean")
        
        return has_hydraulic_lift
    
    # Getter methods
    def get_load_capacity(self) -> float:
        """Get the load capacity in tonnes."""
        return self.__load_capacity
    
    def get_truck_type(self) -> str:
        """Get the truck type."""
        return self.__truck_type
    
    def has_hydraulic_lift(self) -> bool:
        """Check if the truck has hydraulic lift system."""
        return self.__has_hydraulic_lift
    
    # Setter methods
    def set_load_capacity(self, load_capacity: float) -> None:
        """Set the load capacity."""
        self.__load_capacity = self._validate_load_capacity(load_capacity)
    
    def set_truck_type(self, truck_type: str) -> None:
        """Set the truck type."""
        self.__truck_type = self._validate_truck_type(truck_type)
    
    def set_has_hydraulic_lift(self, has_hydraulic_lift: bool) -> None:
        """Set the hydraulic lift flag."""
        self.__has_hydraulic_lift = self._validate_has_hydraulic_lift(has_hydraulic_lift)
    
    def calculate_rental_cost(self, rental_period: RentalPeriod, user_discount: float = 0.0) -> float:
        """
        Calculate the rental cost for a truck.

        Args:
            rental_period (RentalPeriod): The rental period
            user_discount (float): User-specific discount percentage (0.0 to 1.0)

        Returns:
            float: Total rental cost after discounts
        """
        base_cost = self.get_base_rental_cost(rental_period)
        final_cost = self.apply_discount(base_cost, user_discount)

        return round(final_cost, 2)
    
    def get_vehicle_type(self) -> str:
        """Get the type of vehicle."""
        return "Truck"
    
    def __str__(self) -> str:
        """Return a string representation of the truck."""
        availability_status = "Available" if not self.is_currently_rented() else "Rented"
        lift_info = "with Hydraulic Lift" if self.__has_hydraulic_lift else "standard"
        
        return (f"Truck ID: {self.get_vehicle_id()}, {self.get_year()} {self.get_make()} {self.get_model()}, "
                f"Daily Rate: ${self.get_daily_rate():.2f}, {self.__load_capacity}t {self.__truck_type} "
                f"({lift_info}), Status: {availability_status}")