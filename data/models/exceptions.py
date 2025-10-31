"""
Custom exceptions for the Vehicle Rental Application.

This module defines custom exception classes to handle specific error
conditions in the vehicle rental system, providing clear error messages
and appropriate error handling for different failure scenarios.
"""


class VehicleRentalException(Exception):
    """
    Base exception class for all vehicle rental related errors.
    
    This serves as the parent class for all custom exceptions in the
    vehicle rental system, allowing for hierarchical exception handling.
    """
    
    def __init__(self, message: str) -> None:
        """
        Initialize the base exception with a message.
        
        Args:
            message (str): Error message describing the exception
        """
        super().__init__(message)
        self.__message = message
    
    def get_message(self) -> str:
        """Get the error message."""
        return self.__message
    
    def set_message(self, message: str) -> None:
        """Set the error message."""
        self.__message = message


class VehicleNotFoundError(VehicleRentalException):
    """
    Exception raised when a requested vehicle cannot be found in the system.
    
    This exception is thrown when operations are attempted on vehicles
    that don't exist in the rental system's database.
    """
    
    def __init__(self, vehicle_id: str) -> None:
        """
        Initialize with vehicle ID that was not found.
        
        Args:
            vehicle_id (str): The ID of the vehicle that was not found
        """
        super().__init__(f"Vehicle with ID '{vehicle_id}' not found in the system")
        self.__vehicle_id = vehicle_id
    
    def get_vehicle_id(self) -> str:
        """Get the vehicle ID that was not found."""
        return self.__vehicle_id
    
    def set_vehicle_id(self, vehicle_id: str) -> None:
        """Set the vehicle ID."""
        self.__vehicle_id = vehicle_id


class VehicleNotAvailableError(VehicleRentalException):
    """
    Exception raised when a vehicle is not available for the requested rental period.
    
    This exception is thrown when attempting to rent a vehicle that is
    already booked for overlapping dates or is otherwise unavailable.
    """
    
    def __init__(self, vehicle_id: str, start_date: str, end_date: str) -> None:
        """
        Initialize with vehicle ID and requested rental period.
        
        Args:
            vehicle_id (str): The ID of the unavailable vehicle
            start_date (str): Start date of the requested rental period
            end_date (str): End date of the requested rental period
        """
        super().__init__(f"Vehicle '{vehicle_id}' is not available for the period {start_date} to {end_date}")
        self.__vehicle_id = vehicle_id
        self.__start_date = start_date
        self.__end_date = end_date
    
    def get_vehicle_id(self) -> str:
        """Get the vehicle ID."""
        return self.__vehicle_id
    
    def get_start_date(self) -> str:
        """Get the start date."""
        return self.__start_date
    
    def get_end_date(self) -> str:
        """Get the end date."""
        return self.__end_date
    
    def set_vehicle_id(self, vehicle_id: str) -> None:
        """Set the vehicle ID."""
        self.__vehicle_id = vehicle_id
    
    def set_start_date(self, start_date: str) -> None:
        """Set the start date."""
        self.__start_date = start_date
    
    def set_end_date(self, end_date: str) -> None:
        """Set the end date."""
        self.__end_date = end_date


class RenterNotFoundError(VehicleRentalException):
    """
    Exception raised when a requested renter/user cannot be found in the system.
    
    This exception is thrown when operations are attempted on renters
    that don't exist in the rental system's database.
    """
    
    def __init__(self, renter_id: str) -> None:
        """
        Initialize with renter ID that was not found.
        
        Args:
            renter_id (str): The ID of the renter that was not found
        """
        super().__init__(f"Renter with ID '{renter_id}' not found in the system")
        self.__renter_id = renter_id
    
    def get_renter_id(self) -> str:
        """Get the renter ID that was not found."""
        return self.__renter_id
    
    def set_renter_id(self, renter_id: str) -> None:
        """Set the renter ID."""
        self.__renter_id = renter_id


class InvalidRentalPeriodError(VehicleRentalException):
    """
    Exception raised when an invalid rental period is specified.
    
    This exception is thrown when rental periods have invalid dates,
    such as start date after end date, or invalid date formats.
    """
    
    def __init__(self, start_date: str, end_date: str, reason: str = "") -> None:
        """
        Initialize with invalid rental period details.
        
        Args:
            start_date (str): The invalid start date
            end_date (str): The invalid end date
            reason (str): Additional reason for the invalid period
        """
        base_message = f"Invalid rental period: {start_date} to {end_date}"
        if reason:
            base_message += f" - {reason}"
        
        super().__init__(base_message)
        self.__start_date = start_date
        self.__end_date = end_date
        self.__reason = reason
    
    def get_start_date(self) -> str:
        """Get the invalid start date."""
        return self.__start_date
    
    def get_end_date(self) -> str:
        """Get the invalid end date."""
        return self.__end_date
    
    def get_reason(self) -> str:
        """Get the reason for invalidity."""
        return self.__reason
    
    def set_start_date(self, start_date: str) -> None:
        """Set the start date."""
        self.__start_date = start_date
    
    def set_end_date(self, end_date: str) -> None:
        """Set the end date."""
        self.__end_date = end_date
    
    def set_reason(self, reason: str) -> None:
        """Set the reason."""
        self.__reason = reason


class DuplicateVehicleError(VehicleRentalException):
    """
    Exception raised when attempting to add a vehicle with an ID that already exists.
    
    This exception ensures vehicle ID uniqueness in the system.
    """
    
    def __init__(self, vehicle_id: str) -> None:
        """
        Initialize with the duplicate vehicle ID.
        
        Args:
            vehicle_id (str): The ID that already exists in the system
        """
        super().__init__(f"Vehicle with ID '{vehicle_id}' already exists in the system")
        self.__vehicle_id = vehicle_id
    
    def get_vehicle_id(self) -> str:
        """Get the duplicate vehicle ID."""
        return self.__vehicle_id
    
    def set_vehicle_id(self, vehicle_id: str) -> None:
        """Set the vehicle ID."""
        self.__vehicle_id = vehicle_id


class DuplicateRenterError(VehicleRentalException):
    """
    Exception raised when attempting to add a renter with an ID that already exists.
    
    This exception ensures renter ID uniqueness in the system.
    """
    
    def __init__(self, renter_id: str) -> None:
        """
        Initialize with the duplicate renter ID.
        
        Args:
            renter_id (str): The ID that already exists in the system
        """
        super().__init__(f"Renter with ID '{renter_id}' already exists in the system")
        self.__renter_id = renter_id
    
    def get_renter_id(self) -> str:
        """Get the duplicate renter ID."""
        return self.__renter_id
    
    def set_renter_id(self, renter_id: str) -> None:
        """Set the renter ID."""
        self.__renter_id = renter_id


class VehicleAlreadyReturnedError(VehicleRentalException):
    """
    Exception raised when attempting to return a vehicle that is not currently rented.
    
    This exception is thrown when trying to return a vehicle that is
    already available or was never rented.
    """
    
    def __init__(self, vehicle_id: str) -> None:
        """
        Initialize with vehicle ID that cannot be returned.
        
        Args:
            vehicle_id (str): The ID of the vehicle that cannot be returned
        """
        super().__init__(f"Vehicle '{vehicle_id}' is not currently rented and cannot be returned")
        self.__vehicle_id = vehicle_id
    
    def get_vehicle_id(self) -> str:
        """Get the vehicle ID that cannot be returned."""
        return self.__vehicle_id
    
    def set_vehicle_id(self, vehicle_id: str) -> None:
        """Set the vehicle ID."""
        self.__vehicle_id = vehicle_id


class DataPersistenceError(VehicleRentalException):
    """
    Exception raised when data saving or loading operations fail.
    
    This exception is thrown when pickle operations or file I/O
    operations encounter errors during data persistence.
    """
    
    def __init__(self, operation: str, reason: str) -> None:
        """
        Initialize with operation type and failure reason.
        
        Args:
            operation (str): The operation that failed (e.g., 'saving', 'loading')
            reason (str): The reason for the failure
        """
        super().__init__(f"Data persistence error during {operation}: {reason}")
        self.__operation = operation
        self.__reason = reason
    
    def get_operation(self) -> str:
        """Get the operation that failed."""
        return self.__operation
    
    def get_reason(self) -> str:
        """Get the reason for failure."""
        return self.__reason
    
    def set_operation(self, operation: str) -> None:
        """Set the operation."""
        self.__operation = operation
    
    def set_reason(self, reason: str) -> None:
        """Set the reason."""
        self.__reason = reason


class InvalidVehicleDataError(VehicleRentalException):
    """
    Exception raised when vehicle data validation fails.
    
    This exception is thrown when vehicle attributes contain invalid
    values such as negative rates, invalid years, etc.
    """
    
    def __init__(self, field: str, value: str, reason: str) -> None:
        """
        Initialize with invalid field details.
        
        Args:
            field (str): The field that has invalid data
            value (str): The invalid value
            reason (str): Why the value is invalid
        """
        super().__init__(f"Invalid vehicle data - {field}: '{value}' - {reason}")
        self.__field = field
        self.__value = value
        self.__reason = reason
    
    def get_field(self) -> str:
        """Get the field that has invalid data."""
        return self.__field
    
    def get_value(self) -> str:
        """Get the invalid value."""
        return self.__value
    
    def get_reason(self) -> str:
        """Get the reason for invalidity."""
        return self.__reason
    
    def set_field(self, field: str) -> None:
        """Set the field name."""
        self.__field = field
    
    def set_value(self, value: str) -> None:
        """Set the value."""
        self.__value = value
    
    def set_reason(self, reason: str) -> None:
        """Set the reason."""
        self.__reason = reason


class InvalidRenterDataError(VehicleRentalException):
    """
    Exception raised when renter data validation fails.
    
    This exception is thrown when renter attributes contain invalid
    values such as invalid email formats, empty names, etc.
    """
    
    def __init__(self, field: str, value: str, reason: str) -> None:
        """
        Initialize with invalid field details.
        
        Args:
            field (str): The field that has invalid data
            value (str): The invalid value
            reason (str): Why the value is invalid
        """
        super().__init__(f"Invalid renter data - {field}: '{value}' - {reason}")
        self.__field = field
        self.__value = value
        self.__reason = reason
    
    def get_field(self) -> str:
        """Get the field that has invalid data."""
        return self.__field
    
    def get_value(self) -> str:
        """Get the invalid value."""
        return self.__value
    
    def get_reason(self) -> str:
        """Get the reason for invalidity."""
        return self.__reason
    
    def set_field(self, field: str) -> None:
        """Set the field name."""
        self.__field = field
    
    def set_value(self, value: str) -> None:
        """Set the value."""
        self.__value = value
    
    def set_reason(self, reason: str) -> None:
        """Set the reason."""
        self.__reason = reason