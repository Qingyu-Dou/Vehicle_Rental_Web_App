"""
Rental Period module for Vehicle Rental Application.

This module contains the RentalPeriod class that represents a rental period
with start and end dates, and provides methods to calculate duration and
check for overlaps with other rental periods.
"""

from datetime import datetime
from exceptions import InvalidRentalPeriodError


class RentalPeriod:
    """
    Represents a rental period with start and end dates.
    
    This class handles rental period operations including duration calculation
    and overlap detection with other rental periods, with comprehensive
    validation and error handling.

    Year range for rental periods is configurable via MIN_YEAR and MAX_YEAR.
    """
    MIN_YEAR = 2000  # Minimum allowed year for rental period
    MAX_YEAR = 2100  # Maximum allowed year for rental period
    
    def __init__(self, start_date: str, end_date: str, allow_past_dates: bool = False) -> None:
        """
        Initialize a RentalPeriod object.
        
        Args:
            start_date (str): Start date in DD-MM-YYYY format
            end_date (str): End date in DD-MM-YYYY format
            allow_past_dates (bool): Whether to allow past dates (for returns/historical data)
            
        Raises:
            InvalidRentalPeriodError: If date format is invalid or start date is after end date
        """
        try:
            self.__start_date_obj = self._validate_and_parse_date(start_date, "start", allow_past_dates)
            self.__end_date_obj = self._validate_and_parse_date(end_date, "end", allow_past_dates)
            
            # Check that start date is not after end date
            if self.__start_date_obj > self.__end_date_obj:
                raise InvalidRentalPeriodError(start_date, end_date, "Start date cannot be after end date")
            
            # Store original string format for display
            self.__start_date = start_date
            self.__end_date = end_date
            
        except ValueError as e:
            if "InvalidRentalPeriodError" not in str(e):
                raise InvalidRentalPeriodError(start_date, end_date, str(e))
            raise
    
    def _validate_and_parse_date(self, date_str: str, date_type: str, allow_past_dates: bool = False) -> datetime:
        """Validate and parse date string."""
        try:
            # Parse date string; catch invalid dates and format issues
            date_obj = datetime.strptime(date_str.strip(), "%d-%m-%Y")
            
            # Year range check
            year = date_obj.year
            if year < self.MIN_YEAR or year > self.MAX_YEAR:
                raise InvalidRentalPeriodError(date_str, "", f"Invalid {date_type} date: year must be between {self.MIN_YEAR}-{self.MAX_YEAR}")
            
            # Don't allow past dates unless explicitly permitted
            if not allow_past_dates:
                current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                if date_obj < current_date:
                    raise InvalidRentalPeriodError(date_str, "", f"Invalid {date_type} date: cannot be in the past")
            
            return date_obj
        except ValueError as e:
            if "time data" in str(e) or "does not match format" in str(e):
                raise InvalidRentalPeriodError(date_str, "", f"Invalid {date_type} date format: expected DD-MM-YYYY")
            elif "day is out of range for month" in str(e):
                raise InvalidRentalPeriodError(date_str, "", f"Invalid {date_type} date: day does not exist in specified month")
            else:
                raise InvalidRentalPeriodError(date_str, "", f"Invalid {date_type} date: {str(e)}")
    
    # Getter methods
    def get_start_date(self) -> str:
        """Get the start date of the rental period."""
        return self.__start_date
    
    def get_end_date(self) -> str:
        """Get the end date of the rental period."""
        return self.__end_date
    
    def get_start_date_obj(self) -> datetime:
        """Get the start date as datetime object."""
        return self.__start_date_obj
    
    def get_end_date_obj(self) -> datetime:
        """Get the end date as datetime object."""
        return self.__end_date_obj
    
    # Setter methods
    def set_start_date(self, start_date: str, allow_past_dates: bool = False) -> None:
        """Set the start date of the rental period."""
        new_start_obj = self._validate_and_parse_date(start_date, "start", allow_past_dates)
        if new_start_obj > self.__end_date_obj:
            raise InvalidRentalPeriodError(start_date, self.__end_date, "Start date cannot be after end date")
        
        self.__start_date = start_date
        self.__start_date_obj = new_start_obj
    
    def set_end_date(self, end_date: str, allow_past_dates: bool = False) -> None:
        """Set the end date of the rental period."""
        new_end_obj = self._validate_and_parse_date(end_date, "end", allow_past_dates)
        if self.__start_date_obj > new_end_obj:
            raise InvalidRentalPeriodError(self.__start_date, end_date, "End date cannot be before start date")
        
        self.__end_date = end_date
        self.__end_date_obj = new_end_obj
    
    def calculate_duration(self) -> int:
        """Calculate the duration of the rental period in days."""
        duration = (self.__end_date_obj - self.__start_date_obj).days + 1
        return duration
    
    def overlaps_with(self, other: 'RentalPeriod') -> bool:
        """
        Check if this rental period overlaps with another rental period.
        
        Args:
            other (RentalPeriod): Another rental period to check overlap with
            
        Returns:
            bool: True if periods overlap, False otherwise
            
        Raises:
            TypeError: If other is not a RentalPeriod object
        """
        if not isinstance(other, RentalPeriod):
            raise TypeError("Can only check overlap with another RentalPeriod object")
        
        # Check if periods overlap using datetime objects
        return not (self.__end_date_obj < other.get_start_date_obj() or 
                   other.get_end_date_obj() < self.__start_date_obj)
    
    def __str__(self) -> str:
        """Return a string representation of the rental period."""
        duration = self.calculate_duration()
        return f"Rental Period: {self.__start_date} to {self.__end_date} ({duration} days)"
    
    def __eq__(self, other) -> bool:
        """Check equality with another rental period."""
        if not isinstance(other, RentalPeriod):
            return False
        return (self.__start_date_obj == other.get_start_date_obj() and 
                self.__end_date_obj == other.get_end_date_obj())
    
    def __lt__(self, other) -> bool:
        """Check if this period starts before another period."""
        if not isinstance(other, RentalPeriod):
            return NotImplemented
        return self.__start_date_obj < other.get_start_date_obj()