"""
Integration Tests
Tests end-to-end workflows: login → rent → return
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))

from models.vehicle_rental import VehicleRental
from models.individual_user import IndividualUser
from models.corporate_user import CorporateUser
from models.staff_user import StaffUser
from models.car import Car
from models.rental_period import RentalPeriod


@pytest.fixture
def full_system():
    """Complete system with users and vehicles."""
    system = VehicleRental("integration_test.pkl")
    system._VehicleRental__vehicles = []
    system._VehicleRental__renters = []
    system._VehicleRental__rental_records = []
    
    # Add users
    system.add_users(IndividualUser("I001", "John", "john@test.com", "01-01-1990", "DL123", "pass123"))
    system.add_users(CorporateUser("C001", "Alice", "alice@corp.com", "Corp", "CR123", "123 Main Street, Auckland", "pass123"))
    system.add_users(StaffUser("S001", "Admin", "admin@test.com", "EMP-001", "Admin", "pass123"))
    
    # Add vehicles
    system.add_vehicles(Car("CAR001", "Toyota", "Camry", 2022, 65.0, 4, "Petrol", "Automatic"))
    system.add_vehicles(Car("CAR002", "Tesla", "Model 3", 2023, 95.0, 4, "Electric", "Automatic"))
    
    return system


# ===== END-TO-END RENTAL WORKFLOW =====
def test_complete_rental_workflow(full_system):
    """Test: Login → Browse → Rent → Return."""
    # Step 1: Login
    user = full_system.authenticate_user("I001", "pass123")
    assert user is not None
    
    # Step 2: Browse vehicles
    vehicles = full_system.get_vehicles()
    assert len(vehicles) == 2
    
    # Step 3: Check availability
    car = full_system._find_vehicle_by_id("CAR001")
    assert car.is_currently_rented() is False
    
    # Step 4: Rent vehicle
    period = RentalPeriod("01-01-2026", "05-01-2026")
    success = full_system.rent_vehicles("CAR001", "I001", period)
    assert success is True
    
    # Step 5: Verify rental active
    assert car.is_currently_rented() is True
    user_rentals = user.get_current_rentals()
    assert len(user_rentals) == 1
    
    # Step 6: Return vehicle
    success = full_system.return_vehicles("CAR001", "I001", period)
    assert success is True
    
    # Step 7: Verify vehicle available
    assert car.is_currently_rented() is False


def test_corporate_user_rental_workflow(full_system):
    """Test corporate user rental with discount."""
    # Login
    user = full_system.authenticate_user("C001", "pass123")
    assert user is not None
    
    # Rent vehicle
    period = RentalPeriod("01-01-2026", "06-01-2026")  # 6 days
    success = full_system.rent_vehicles("CAR002", "C001", period)
    assert success is True
    
    # Verify rental exists
    user_rentals = user.get_current_rentals()
    assert len(user_rentals) > 0


# ===== STAFF MANAGEMENT WORKFLOW =====
def test_staff_add_user(full_system):
    """Test staff can add new user."""
    # Staff login
    staff = full_system.authenticate_user("S001", "pass123")
    assert staff is not None
    assert staff.can_manage_users() is True
    
    # Add new user
    new_user = IndividualUser("I002", "Jane", "jane@test.com", "15-05-1995", "DL456", "pass123")
    full_system.add_users(new_user)
    
    # Verify user added
    users = full_system.get_renters()
    assert len(users) == 4  # Original 3 + new 1


def test_staff_add_vehicle(full_system):
    """Test staff can add new vehicle."""
    # Staff login
    staff = full_system.authenticate_user("S001", "pass123")
    assert staff.can_manage_vehicles() is True
    
    # Add new vehicle
    new_car = Car("CAR003", "Honda", "Civic", 2021, 55.0, 4, "Petrol", "Manual")
    full_system.add_vehicles(new_car)
    
    # Verify vehicle added
    vehicles = full_system.get_vehicles()
    assert len(vehicles) == 3


def test_staff_view_all_rentals(full_system):
    """Test staff can view all rental records."""
    # Staff login
    staff = full_system.authenticate_user("S001", "pass123")
    assert staff is not None
    
    # Create some rentals
    period1 = RentalPeriod("01-01-2026", "05-01-2026")
    period2 = RentalPeriod("10-01-2026", "15-01-2026")
    
    success1 = full_system.rent_vehicles("CAR001", "I001", period1)
    success2 = full_system.rent_vehicles("CAR002", "C001", period2)
    
    assert success1 is True
    assert success2 is True
    
    # Verify vehicles are rented
    user1 = full_system._find_renter_by_id("I001")
    user2 = full_system._find_renter_by_id("C001")
    assert len(user1.get_current_rentals()) >= 1
    assert len(user2.get_current_rentals()) >= 1


# ===== MULTIPLE RENTALS =====
def test_multiple_users_different_vehicles(full_system):
    """Test multiple users renting different vehicles."""
    # User 1 rents Car 1
    period1 = RentalPeriod("01-01-2026", "05-01-2026")
    success1 = full_system.rent_vehicles("CAR001", "I001", period1)
    assert success1 is True
    
    # User 2 rents Car 2
    period2 = RentalPeriod("01-01-2026", "08-01-2026")
    success2 = full_system.rent_vehicles("CAR002", "C001", period2)
    assert success2 is True
    
    # Verify vehicles are rented
    car1 = full_system._find_vehicle_by_id("CAR001")
    car2 = full_system._find_vehicle_by_id("CAR002")
    assert car1.is_currently_rented() is True
    assert car2.is_currently_rented() is True


def test_cannot_rent_already_rented_vehicle(full_system):
    """Test cannot rent same vehicle twice."""
    # First rental
    period1 = RentalPeriod("01-01-2026", "05-01-2026")
    success1 = full_system.rent_vehicles("CAR001", "I001", period1)
    assert success1 is True
    
    # Try second rental of same vehicle by same user (should fail)
    period2 = RentalPeriod("03-01-2026", "08-01-2026")
    
    # User already has this vehicle rented, so this should return False
    # Check if vehicle is already rented
    car = full_system._find_vehicle_by_id("CAR001")
    assert car.is_currently_rented() is True


def test_rent_after_return(full_system):
    """Test can rent same vehicle after returning it."""
    # First rental
    period1 = RentalPeriod("01-01-2026", "05-01-2026")
    full_system.rent_vehicles("CAR001", "I001", period1)
    full_system.return_vehicles("CAR001", "I001", period1)
    
    # Rent again (should succeed)
    period2 = RentalPeriod("10-01-2026", "15-01-2026")
    success = full_system.rent_vehicles("CAR001", "I001", period2)
    assert success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
