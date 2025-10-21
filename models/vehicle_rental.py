"""
Vehicle Rental module for Vehicle Rental Application.

This module contains the VehicleRental class that manages the collection of vehicles
and renters, providing methods for rental operations with comprehensive validation,
data persistence using pickle, and support for multiple rentals per vehicle.
"""

import pickle
import os
from typing import List, Optional
from datetime import datetime
from vehicle import Vehicle
from car import Car
from motorbike import Motorbike
from truck import Truck
from renter import Renter
from individual_user import IndividualUser
from corporate_user import CorporateUser
from staff_user import StaffUser
from rental_period import RentalPeriod
from rental_record import RentalRecord
from exceptions import (
    VehicleNotFoundError, RenterNotFoundError, VehicleNotAvailableError,
    DuplicateVehicleError, DuplicateRenterError, VehicleAlreadyReturnedError,
    DataPersistenceError
)


class VehicleRental:
    """
    Manages the vehicle rental system including vehicles, renters, and rental operations.
    
    This class provides functionality to add vehicles and renters, manage multiple
    rentals per vehicle, display system information, and includes comprehensive
    validation, error handling, and data persistence using pickle.
    """
    
    def __init__(self, data_file: str = "vehicle_rental_data.pkl") -> None:
        """
        Initialize the VehicleRental system.
        
        Args:
            data_file (str): Path to the data persistence file
        """
        self.__vehicles: List[Vehicle] = []
        self.__renters: List[Renter] = []
        self.__rental_records: List[RentalRecord] = []
        self.__data_file = data_file
        self.__next_record_id = 1  # Counter for generating rental record IDs
        
        # Load existing data on startup
        self.load_data()
    
    def save_data(self) -> None:
        """
        Save all system data to a pickle file.
        
        Raises:
            DataPersistenceError: If saving fails
        """
        try:
            data = {
                'vehicles': self.__vehicles,
                'renters': self.__renters,
                'rental_records': self.__rental_records,
                'next_record_id': self.__next_record_id,
                'save_timestamp': datetime.now().isoformat(),
                'version': '3.0'
            }
            
            with open(self.__data_file, 'wb') as file:
                pickle.dump(data, file)
            
            print(f"Data successfully saved to {self.__data_file}")
            
        except (IOError, pickle.PickleError, OSError) as e:
            raise DataPersistenceError("saving", str(e))
    
    def load_data(self) -> None:
        """
        Load system data from a pickle file.
        
        Raises:
            DataPersistenceError: If loading fails critically
        """
        try:
            if not os.path.exists(self.__data_file):
                print("No existing data file found. Starting with empty system.")
                return
            
            with open(self.__data_file, 'rb') as file:
                data = pickle.load(file)
            
            # Load vehicles
            if 'vehicles' in data and isinstance(data['vehicles'], list):
                self.__vehicles = data['vehicles']
            else:
                self.__vehicles = []
            
            # Load renters
            if 'renters' in data and isinstance(data['renters'], list):
                self.__renters = data['renters']
            else:
                self.__renters = []
            
            # Load rental records
            if 'rental_records' in data and isinstance(data['rental_records'], list):
                self.__rental_records = data['rental_records']
            else:
                self.__rental_records = []
            
            # Load next record ID
            if 'next_record_id' in data:
                self.__next_record_id = data['next_record_id']
            else:
                self.__next_record_id = 1
            
            print(f"Data successfully loaded. {len(self.__vehicles)} vehicles, {len(self.__renters)} renters, and {len(self.__rental_records)} rental records.")
                
        except FileNotFoundError:
            print("Data file not found. Starting with empty system.")
        except (IOError, pickle.PickleError, EOFError) as e:
            print(f"Warning: Could not load data: {e}")
            print("Starting with empty system.")
            self.__vehicles = []
            self.__renters = []
            self.__rental_records = []
            self.__next_record_id = 1
    
    def _find_vehicle_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        """Find a vehicle by its ID."""
        for vehicle in self.__vehicles:
            if vehicle.get_vehicle_id() == vehicle_id:
                return vehicle
        return None
    
    def _find_renter_by_id(self, renter_id: str) -> Optional[Renter]:
        """Find a renter by their ID."""
        for renter in self.__renters:
            if renter.get_renter_id() == renter_id:
                return renter
        return None
    
    def add_vehicles(self, vehicle: Vehicle) -> None:
        """
        Add a new vehicle to the rental system.
        
        Args:
            vehicle (Vehicle): Vehicle object to add to the system
            
        Raises:
            DuplicateVehicleError: If vehicle ID already exists
            TypeError: If vehicle is not a Vehicle object
        """
        if not isinstance(vehicle, Vehicle):
            raise TypeError("Input must be a Vehicle object")
        
        vehicle_id = vehicle.get_vehicle_id()
        if self._find_vehicle_by_id(vehicle_id) is not None:
            raise DuplicateVehicleError(vehicle_id)
        
        self.__vehicles.append(vehicle)
        print(f"Vehicle {vehicle_id} ({vehicle.get_vehicle_type()}) added to the system.")
        
        # Auto-save after adding vehicle
        try:
            self.save_data()
        except DataPersistenceError as e:
            print(f"Warning: Could not save data after adding vehicle: {e}")
    
    def add_users(self, renter: Renter) -> None:
        """
        Add a new renter to the rental system.
        
        Args:
            renter (Renter): Renter object to add to the system
            
        Raises:
            DuplicateRenterError: If renter ID already exists
            TypeError: If renter is not a Renter object
        """
        if not isinstance(renter, Renter):
            raise TypeError("Input must be a Renter object")
        
        renter_id = renter.get_renter_id()
        if self._find_renter_by_id(renter_id) is not None:
            raise DuplicateRenterError(renter_id)
        
        self.__renters.append(renter)
        print(f"{renter.get_user_type()} user {renter.get_name()} (ID: {renter_id}) added to the system.")
        
        # Auto-save after adding renter
        try:
            self.save_data()
        except DataPersistenceError as e:
            print(f"Warning: Could not save data after adding renter: {e}")
    
    def rent_vehicles(self, vehicle_id: str, renter_id: str, rental_period: RentalPeriod) -> bool:
        """
        Rent a vehicle to a renter for a specified period.
        
        Args:
            vehicle_id (str): ID of the vehicle to rent
            renter_id (str): ID of the renter
            rental_period (RentalPeriod): Period for which to rent the vehicle
            
        Returns:
            bool: True if rental successful, False otherwise
        """
        try:
            # Find vehicle and renter
            vehicle = self._find_vehicle_by_id(vehicle_id)
            if vehicle is None:
                raise VehicleNotFoundError(vehicle_id)
            
            renter = self._find_renter_by_id(renter_id)
            if renter is None:
                raise RenterNotFoundError(renter_id)
            
            # Check if renter can rent more vehicles
            if not renter.can_rent_vehicle():
                print(f"Error: Renter {renter_id} has reached maximum concurrent rentals.")
                return False
            
            # Check vehicle availability
            if not vehicle.is_available(rental_period):
                raise VehicleNotAvailableError(
                    vehicle_id,
                    rental_period.get_start_date(),
                    rental_period.get_end_date()
                )
            
            # Calculate rental cost with user-specific discount
            user_discount = renter.calculate_discount(rental_period)
            rental_cost = vehicle.calculate_rental_cost(rental_period, user_discount)
            
            # Add rental to vehicle and renter
            vehicle.add_rental(rental_period, renter_id)
            renter.add_rental(vehicle_id, rental_period, rental_cost)
            
            # Display rental confirmation
            duration = rental_period.calculate_duration()
            discount_pct = user_discount * 100
            
            print(f"\n{'='*60}")
            print(f"RENTAL CONFIRMATION")
            print(f"{'='*60}")
            print(f"Vehicle ID: {vehicle.get_vehicle_id()}")
            print(f"Vehicle: {vehicle.get_year()} {vehicle.get_make()} {vehicle.get_model()} ({vehicle.get_vehicle_type()})")
            print(f"Renter: {renter.get_name()} ({renter.get_user_type()})")
            print(f"Period: {rental_period.get_start_date()} to {rental_period.get_end_date()}")
            print(f"Duration: {duration} days")
            print(f"Discount Applied: {discount_pct:.1f}%")
            print(f"Total Cost: ${rental_cost:.2f}")
            print(f"{'='*60}")
            
            # Auto-save after successful rental
            try:
                self.save_data()
            except DataPersistenceError as e:
                print(f"Warning: Could not save data after rental: {e}")
            
            return True
            
        except (VehicleNotFoundError, RenterNotFoundError, VehicleNotAvailableError) as e:
            print(f"Error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during rental: {e}")
            return False
    
    def return_vehicles(self, vehicle_id: str, renter_id: str, rental_period: RentalPeriod) -> bool:
        """
        Return a rented vehicle.
        
        Args:
            vehicle_id (str): ID of the vehicle to return
            renter_id (str): ID of the renter returning the vehicle
            rental_period (RentalPeriod): Rental period being completed
            
        Returns:
            bool: True if return successful, False otherwise
        """
        try:
            # Find vehicle and renter
            vehicle = self._find_vehicle_by_id(vehicle_id)
            if vehicle is None:
                raise VehicleNotFoundError(vehicle_id)
            
            renter = self._find_renter_by_id(renter_id)
            if renter is None:
                raise RenterNotFoundError(renter_id)
            
            # Check if vehicle is currently rented
            if not vehicle.is_currently_rented():
                raise VehicleAlreadyReturnedError(vehicle_id)
            
            # Remove rental from vehicle
            if not vehicle.remove_rental(rental_period):
                print(f"Error: Could not find matching rental period for vehicle {vehicle_id}.")
                return False
            
            # Complete rental in renter's records
            if not renter.complete_rental(vehicle_id, rental_period):
                print(f"Error: Could not find matching rental in renter's records.")
                # Try to restore vehicle rental state
                vehicle.add_rental(rental_period, renter_id)
                return False
            
            print(f"\n{'='*60}")
            print(f"RETURN CONFIRMATION")
            print(f"{'='*60}")
            print(f"Vehicle ID: {vehicle_id}")
            print(f"Vehicle: {vehicle.get_year()} {vehicle.get_make()} {vehicle.get_model()} ({vehicle.get_vehicle_type()})")
            print(f"Returned by: {renter.get_name()}")
            print(f"Rental period: {rental_period.get_start_date()} to {rental_period.get_end_date()}")
            print(f"{'='*60}")
            
            # Auto-save after successful return
            try:
                self.save_data()
            except DataPersistenceError as e:
                print(f"Warning: Could not save data after return: {e}")
            
            return True
            
        except (VehicleNotFoundError, RenterNotFoundError, VehicleAlreadyReturnedError) as e:
            print(f"Error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during return: {e}")
            return False
    
    def display_available_vehicles(self) -> None:
        """Display all available vehicles in the system."""
        available_vehicles = [v for v in self.__vehicles if not v.is_currently_rented()]
        
        if not available_vehicles:
            print("\nNo available vehicles in the system.")
            return
        
        print(f"\n{'='*80}")
        print(f"AVAILABLE VEHICLES ({len(available_vehicles)} total)")
        print(f"{'='*80}")
        
        # Group by vehicle type
        cars = [v for v in available_vehicles if isinstance(v, Car)]
        motorbikes = [v for v in available_vehicles if isinstance(v, Motorbike)]
        trucks = [v for v in available_vehicles if isinstance(v, Truck)]
        
        for vehicle_type, vehicles in [("CARS", cars), ("MOTORBIKES", motorbikes), ("TRUCKS", trucks)]:
            if vehicles:
                print(f"\n{vehicle_type}:")
                print("-" * 40)
                for vehicle in vehicles:
                    print(f"  {vehicle}")
    
    def display_vehicles_on_rent(self) -> None:
        """Display all currently rented vehicles with rental information."""
        rented_vehicles = [v for v in self.__vehicles if v.is_currently_rented()]
        
        if not rented_vehicles:
            print("\nNo vehicles currently rented.")
            return
        
        print(f"\n{'='*80}")
        print(f"RENTED VEHICLES ({len(rented_vehicles)} total)")
        print(f"{'='*80}")
        
        for vehicle in rented_vehicles:
            print(f"\n{vehicle}")
            rental_periods = vehicle.get_rental_periods()
            
            for period in rental_periods:
                # Find the renter for this period
                renter = None
                for r in self.__renters:
                    for rental in r.get_current_rentals():
                        if (rental['vehicle_id'] == vehicle.get_vehicle_id() and
                            rental['start_date'] == period['start_date'] and
                            rental['end_date'] == period['end_date']):
                            renter = r
                            break
                    if renter:
                        break
                
                if renter:
                    print(f"  Rented to: {renter.get_name()} ({renter.get_user_type()})")
                    print(f"  Period: {period['start_date']} to {period['end_date']}")
                    # Find rental cost from renter's records
                    for rental in renter.get_current_rentals():
                        if (rental['vehicle_id'] == vehicle.get_vehicle_id() and
                            rental['start_date'] == period['start_date']):
                            print(f"  Cost: ${rental['cost']:.2f}")
                            break
                print("-" * 50)
    
    def display_users(self) -> None:
        """Display all users in the system."""
        if not self.__renters:
            print("\nNo users in the system.")
            return
        
        print(f"\n{'='*80}")
        print(f"ALL USERS ({len(self.__renters)} total)")
        print(f"{'='*80}")
        
        # Group by user type
        individuals = [r for r in self.__renters if isinstance(r, IndividualUser)]
        corporates = [r for r in self.__renters if isinstance(r, CorporateUser)]
        
        if individuals:
            print(f"\nINDIVIDUAL USERS ({len(individuals)}):")
            print("-" * 50)
            for renter in individuals:
                print(f"  {renter}")
        
        if corporates:
            print(f"\nCORPORATE USERS ({len(corporates)}):")
            print("-" * 50)
            for renter in corporates:
                print(f"  {renter}")
    
    def get_vehicles(self) -> List[Vehicle]:
        """Get a copy of the vehicles list."""
        return self.__vehicles.copy()
    
    def get_renters(self) -> List[Renter]:
        """Get a copy of the renters list."""
        return self.__renters.copy()
    
    def get_rental_records(self) -> List[RentalRecord]:
        """Get a copy of all rental records."""
        return self.__rental_records.copy()
    
    def add_rental_record(self, vehicle_id: str, renter_id: str, start_date: str, 
                         end_date: str, rental_cost: float, discount_applied: float = 0.0) -> RentalRecord:
        """
        Create and add a new rental record to the system.
        
        Args:
            vehicle_id (str): ID of the rented vehicle
            renter_id (str): ID of the renter
            start_date (str): Rental start date
            end_date (str): Rental end date
            rental_cost (float): Total rental cost
            discount_applied (float): Discount percentage applied
            
        Returns:
            RentalRecord: The created rental record
        """
        record_id = f"R{self.__next_record_id:05d}"
        self.__next_record_id += 1
        
        rental_record = RentalRecord(
            record_id=record_id,
            vehicle_id=vehicle_id,
            renter_id=renter_id,
            start_date=start_date,
            end_date=end_date,
            rental_cost=rental_cost,
            status='active',
            discount_applied=discount_applied
        )
        
        self.__rental_records.append(rental_record)
        return rental_record
    
    def get_rental_records_by_vehicle(self, vehicle_id: str) -> List[RentalRecord]:
        """Get all rental records for a specific vehicle."""
        return [r for r in self.__rental_records if r.get_vehicle_id() == vehicle_id]
    
    def get_rental_records_by_renter(self, renter_id: str) -> List[RentalRecord]:
        """Get all rental records for a specific renter."""
        return [r for r in self.__rental_records if r.get_renter_id() == renter_id]
    
    def get_active_rental_records(self) -> List[RentalRecord]:
        """Get all currently active rental records."""
        return [r for r in self.__rental_records if r.is_active()]
    
    def find_rental_record_by_id(self, record_id: str) -> Optional[RentalRecord]:
        """Find a rental record by its ID."""
        for record in self.__rental_records:
            if record.get_record_id() == record_id:
                return record
        return None
    
    def authenticate_user(self, renter_id: str, password: str) -> Optional[Renter]:
        """
        Authenticate a user with their ID and password.
        
        Args:
            renter_id (str): User ID
            password (str): Password
            
        Returns:
            Optional[Renter]: The authenticated user object if successful, None otherwise
        """
        renter = self._find_renter_by_id(renter_id)
        if renter and renter.verify_password(password):
            return renter
        return None
    
    def cleanup_and_exit(self) -> None:
        """Perform cleanup operations and save data before exiting."""
        try:
            print("\nPerforming final data save...")
            self.save_data()
            print("System shutdown complete.")
        except DataPersistenceError as e:
            print(f"Error during final save: {e}")
    
    def __del__(self) -> None:
        """Destructor to ensure data is saved when object is destroyed."""
        try:
            self.save_data()
        except:
            pass  # Avoid exceptions during destruction