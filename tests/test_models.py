"""
Unit Tests
Tests: User authentication, Discount calculation, Rental logic
"""

import pytest
import sys
import os

# Add models directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
models_path = os.path.join(project_root, 'models')

if models_path not in sys.path:
    sys.path.insert(0, models_path)

# Import from models directory
import vehicle_rental
import individual_user
import corporate_user
import staff_user
import car
import rental_period

VehicleRental = vehicle_rental.VehicleRental
IndividualUser = individual_user.IndividualUser
CorporateUser = corporate_user.CorporateUser
StaffUser = staff_user.StaffUser
Car = car.Car
RentalPeriod = rental_period.RentalPeriod


@pytest.fixture
def system():
    """Fresh rental system for each test."""
    s = VehicleRental("test_data.pkl")
    s._VehicleRental__vehicles = []
    s._VehicleRental__renters = []
    s._VehicleRental__rental_records = []
    return s


# ===== USER AUTHENTICATION TESTS =====
def test_individual_login(system):
    """Test individual user can login."""
    user = IndividualUser("I001", "John", "john@test.com", "01-01-1990", "DL123", "pass123")
    system.add_users(user)
    auth_user = system.authenticate_user("I001", "pass123")
    assert auth_user is not None
    assert auth_user.get_renter_id() == "I001"


def test_corporate_login(system):
    """Test corporate user can login."""
    user = CorporateUser("C001", "Alice", "alice@corp.com", "Corp", "CR123", "123 Main Street, Auckland", "pass123")
    system.add_users(user)
    auth_user = system.authenticate_user("C001", "pass123")
    assert auth_user is not None


def test_staff_login(system):
    """Test staff user can login."""
    user = StaffUser("S001", "Admin", "admin@test.com", "EMP-001", "Admin", "pass123")
    system.add_users(user)
    auth_user = system.authenticate_user("S001", "pass123")
    assert auth_user is not None


def test_wrong_password(system):
    """Test login fails with wrong password."""
    user = IndividualUser("I001", "John", "john@test.com", "01-01-1990", "DL123", "pass123")
    system.add_users(user)
    auth_user = system.authenticate_user("I001", "wrongpass")
    assert auth_user is None


# ===== DISCOUNT CALCULATION TESTS =====
def test_individual_no_discount_short():
    """Individual user: no discount for rental < 7 days."""
    user = IndividualUser("I001", "John", "john@test.com", "01-01-1990", "DL123", "pass123")
    period = RentalPeriod("01-01-2026", "05-01-2026")  # 4 days
    discount = user.calculate_discount(period)
    assert discount == 0.0


def test_individual_discount_long():
    """Individual user: 10% discount for rental >= 7 days."""
    user = IndividualUser("I001", "John", "john@test.com", "01-01-1990", "DL123", "pass123")
    period = RentalPeriod("01-01-2026", "10-01-2026")  # 9 days
    discount = user.calculate_discount(period)
    assert discount == 0.10  # 10%


def test_corporate_discount():
    """Corporate user: always 15% discount."""
    user = CorporateUser("C001", "Alice", "alice@corp.com", "Corp", "CR123", "123 Main Street, Auckland", "pass123")
    period = RentalPeriod("01-01-2026", "05-01-2026")  # any days
    discount = user.calculate_discount(period)
    assert discount == 0.15  # 15%


def test_staff_no_discount():
    """Staff user: no discount."""
    user = StaffUser("S001", "Admin", "admin@test.com", "EMP-001", "Admin", "pass123")
    period = RentalPeriod("01-01-2026", "10-01-2026")
    discount = user.calculate_discount(period)
    assert discount == 0.0


# ===== RENTAL LOGIC TESTS =====
def test_rent_available_vehicle(system):
    """Test renting an available vehicle."""
    car = Car("C001", "Toyota", "Camry", 2022, 65.0, 4, "Petrol", "Automatic")
    user = IndividualUser("I001", "John", "john@test.com", "01-01-1990", "DL123", "pass123")
    system.add_vehicles(car)
    system.add_users(user)
    
    period = RentalPeriod("01-01-2026", "05-01-2026")
    success = system.rent_vehicles("C001", "I001", period)
    
    assert success is True
    assert car.is_currently_rented() is True


def test_return_vehicle(system):
    """Test returning a rented vehicle."""
    car = Car("C001", "Toyota", "Camry", 2022, 65.0, 4, "Petrol", "Automatic")
    user = IndividualUser("I001", "John", "john@test.com", "01-01-1990", "DL123", "pass123")
    system.add_vehicles(car)
    system.add_users(user)
    
    period = RentalPeriod("01-01-2026", "05-01-2026")
    system.rent_vehicles("C001", "I001", period)
    success = system.return_vehicles("C001", "I001", period)
    
    assert success is True
    assert car.is_currently_rented() is False


def test_rental_cost_calculation(system):
    """Test rental cost is calculated correctly."""
    car = Car("C001", "Toyota", "Camry", 2022, 65.0, 4, "Petrol", "Automatic")
    user = IndividualUser("I001", "John", "john@test.com", "01-01-1990", "DL123", "pass123")
    system.add_vehicles(car)
    system.add_users(user)
    
    period = RentalPeriod("01-01-2026", "05-01-2026")  # 5 days (inclusive)
    system.rent_vehicles("C001", "I001", period)
    
    user_rentals = user.get_current_rentals()
    assert len(user_rentals) > 0
    # 5 days * $65 + 5% GST = $341.25
    assert user_rentals[0]['cost'] == 341.25


def test_rental_with_corporate_discount(system):
    """Test rental cost includes corporate discount."""
    car = Car("C001", "Toyota", "Camry", 2022, 65.0, 4, "Petrol", "Automatic")
    user = CorporateUser("C001", "Alice", "alice@corp.com", "Corp", "CR123", "123 Main Street, Auckland", "pass123")
    system.add_vehicles(car)
    system.add_users(user)
    
    period = RentalPeriod("01-01-2026", "05-01-2026")  # 5 days
    system.rent_vehicles("C001", "C001", period)
    
    user_rentals = user.get_current_rentals()
    # 5 days * $65 * 0.85 (15% discount) + 5% GST
    base = 325.0 * 0.85  # $276.25
    with_gst = base * 1.05  # $290.0625
    assert abs(user_rentals[0]['cost'] - with_gst) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
