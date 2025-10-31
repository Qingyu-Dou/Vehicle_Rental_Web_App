"""
Car module for Vehicle Rental Application.

This module contains the Car class that represents a car in the rental system,
extending the abstract Vehicle class with car-specific attributes and methods.
"""

from vehicle import Vehicle
from rental_period import RentalPeriod
from exceptions import InvalidVehicleDataError


class Car(Vehicle):
    """
    Represents a car in the vehicle rental system.
    
    This class extends the Vehicle base class with car-specific attributes
    such as number of doors, fuel type, and transmission type, and implements
    car-specific rental cost calculations.
    """
    
    def __init__(self, vehicle_id: str, make: str, model: str, year: int, daily_rate: float,
                 num_doors: int, fuel_type: str, transmission: str, image_filename: str = 'default.jpg') -> None:
        """
        Initialize a Car object.

        Args:
            vehicle_id (str): Unique identifier for the car
            make (str): Manufacturer of the car
            model (str): Model of the car
            year (int): Year the car was manufactured
            daily_rate (float): Daily rental rate for the car
            num_doors (int): Number of doors (2, 4, or 5)
            fuel_type (str): Type of fuel (Petrol, Diesel, Electric, Hybrid)
            transmission (str): Transmission type (Manual, Automatic, CVT)
            image_filename (str): Filename of the vehicle image (default: 'default.jpg')

        Raises:
            InvalidVehicleDataError: If any car-specific parameter is invalid
        """
        super().__init__(vehicle_id, make, model, year, daily_rate, image_filename)

        self.__num_doors = self._validate_num_doors(num_doors)
        self.__fuel_type = self._validate_fuel_type(fuel_type)
        self.__transmission = self._validate_transmission(transmission)
    
    def _validate_num_doors(self, num_doors: int) -> int:
        """Validate number of doors."""
        if not isinstance(num_doors, int):
            raise InvalidVehicleDataError("num_doors", str(num_doors), "must be an integer")
        
        if num_doors not in [2, 3, 4, 5]:
            raise InvalidVehicleDataError("num_doors", str(num_doors), "must be 2, 3, 4, or 5")
        
        return num_doors
    
    def _validate_fuel_type(self, fuel_type: str) -> str:
        """Validate fuel type."""
        if not isinstance(fuel_type, str):
            raise InvalidVehicleDataError("fuel_type", str(fuel_type), "must be a string")
        
        fuel_type = fuel_type.strip().title()
        valid_fuel_types = ["Petrol", "Diesel", "Electric", "Hybrid"]
        
        if fuel_type not in valid_fuel_types:
            raise InvalidVehicleDataError(
                "fuel_type", fuel_type, 
                f"must be one of {', '.join(valid_fuel_types)}"
            )
        
        return fuel_type
    
    def _validate_transmission(self, transmission: str) -> str:
        """Validate transmission type."""
        if not isinstance(transmission, str):
            raise InvalidVehicleDataError("transmission", str(transmission), "must be a string")
        
        transmission = transmission.strip().title()
        valid_transmissions = ["Manual", "Automatic", "CVT"]
        
        if transmission not in valid_transmissions:
            raise InvalidVehicleDataError(
                "transmission", transmission,
                f"must be one of {', '.join(valid_transmissions)}"
            )
        
        return transmission
    
    # Getter methods
    def get_num_doors(self) -> int:
        """Get the number of doors."""
        return self.__num_doors
    
    def get_fuel_type(self) -> str:
        """Get the fuel type."""
        return self.__fuel_type
    
    def get_transmission(self) -> str:
        """Get the transmission type."""
        return self.__transmission
    
    # Setter methods
    def set_num_doors(self, num_doors: int) -> None:
        """Set the number of doors."""
        self.__num_doors = self._validate_num_doors(num_doors)
    
    def set_fuel_type(self, fuel_type: str) -> None:
        """Set the fuel type."""
        self.__fuel_type = self._validate_fuel_type(fuel_type)
    
    def set_transmission(self, transmission: str) -> None:
        """Set the transmission type."""
        self.__transmission = self._validate_transmission(transmission)
    
    def calculate_rental_cost(self, rental_period: RentalPeriod, user_discount: float = 0.0) -> float:
        """
        Calculate the rental cost for a car.

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
        return "Car"
    
    def __str__(self) -> str:
        """Return a string representation of the car."""
        availability_status = "Available" if not self.is_currently_rented() else "Rented"
        
        return (f"Car ID: {self.get_vehicle_id()}, {self.get_year()} {self.get_make()} {self.get_model()}, "
                f"Daily Rate: ${self.get_daily_rate():.2f}, {self.__num_doors}-door {self.__fuel_type} "
                f"({self.__transmission}), Status: {availability_status}")