"""
Routes Controller for Vehicle Rental Application.

Handles all HTTP routes and business logic for the web application.
"""

from flask import render_template, request, redirect, url_for, session, flash
from functools import wraps
import sys
import os

# Add models to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))

from models.vehicle_rental import VehicleRental
from models.individual_user import IndividualUser
from models.corporate_user import CorporateUser
from models.staff_user import StaffUser
from models.car import Car
from models.motorbike import Motorbike
from models.truck import Truck
from models.rental_period import RentalPeriod
from datetime import datetime

# Initialize rental system
rental_system = VehicleRental("data/rental_data.pkl")


def init_routes(app):
    """Initialize all routes for the Flask application."""
    
    # ============ Authentication Decorator ============
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login first.', 'error')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def staff_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_type' not in session or session['user_type'] != 'Staff':
                flash('Access denied. Staff only.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    
    # ============ Home & Login Routes ============
    @app.route('/')
    def index():
        """Redirect to login page."""
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Handle user login."""
        if request.method == 'POST':
            user_id = request.form.get('user_id')
            password = request.form.get('password')
            
            # Authenticate user
            user = rental_system.authenticate_user(user_id, password)
            
            if user:
                session['user_id'] = user.get_renter_id()
                session['user_name'] = user.get_name()
                session['user_type'] = user.get_user_type()
                flash(f'Welcome, {user.get_name()}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials. Try again.', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """Handle user logout."""
        session.clear()
        flash('Logged out successfully.', 'success')
        return redirect(url_for('login'))
    
    # ============ Dashboard Routes ============
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Display role-specific dashboard."""
        user_type = session.get('user_type')
        user_id = session.get('user_id')
        
        # Get user object
        user = rental_system._find_renter_by_id(user_id)
        
        if user_type == 'Staff':
            # Staff dashboard with analytics
            vehicles = rental_system.get_vehicles()
            users = rental_system.get_renters()
            records = rental_system.get_rental_records()
            active_records = rental_system.get_active_rental_records()
            
            return render_template('dashboard_staff.html',
                                 user=user,
                                 vehicle_count=len(vehicles),
                                 user_count=len(users),
                                 rental_count=len(records),
                                 active_count=len(active_records))
        else:
            # Individual/Corporate dashboard
            user_rentals = rental_system.get_rental_records_by_renter(user_id)
            active_rentals = [r for r in user_rentals if r.is_active()]
            
            return render_template('dashboard_user.html',
                                 user=user,
                                 active_rentals=active_rentals,
                                 total_rentals=len(user_rentals))
    
    # ============ Vehicle Routes ============
    @app.route('/vehicles')
    @login_required
    def vehicles():
        """Display all vehicles with search/filter."""
        # Get filter parameters
        vehicle_type = request.args.get('type', '')
        brand = request.args.get('brand', '')
        price_range = request.args.get('price', '')
        
        # Get all vehicles
        all_vehicles = rental_system.get_vehicles()
        
        # Apply filters
        filtered_vehicles = all_vehicles
        
        if vehicle_type:
            filtered_vehicles = [v for v in filtered_vehicles if v.get_vehicle_type() == vehicle_type]
        
        if brand:
            filtered_vehicles = [v for v in filtered_vehicles if brand.lower() in v.get_make().lower()]
        
        if price_range:
            if price_range == '0-50':
                filtered_vehicles = [v for v in filtered_vehicles if v.get_daily_rate() <= 50]
            elif price_range == '51-100':
                filtered_vehicles = [v for v in filtered_vehicles if 51 <= v.get_daily_rate() <= 100]
            elif price_range == '101+':
                filtered_vehicles = [v for v in filtered_vehicles if v.get_daily_rate() > 100]
        
        return render_template('vehicles.html',
                             vehicles=filtered_vehicles,
                             current_type=vehicle_type,
                             current_brand=brand,
                             current_price=price_range)
    
    @app.route('/vehicle/<vehicle_id>')
    @login_required
    def vehicle_detail(vehicle_id):
        """Display vehicle details."""
        vehicle = rental_system._find_vehicle_by_id(vehicle_id)
        if not vehicle:
            flash('Vehicle not found.', 'error')
            return redirect(url_for('vehicles'))
        
        return render_template('vehicle_detail.html', vehicle=vehicle)
    
    # ============ Rental Routes ============
    @app.route('/rent/<vehicle_id>', methods=['GET', 'POST'])
    @login_required
    def rent_vehicle(vehicle_id):
        """Handle vehicle rental."""
        vehicle = rental_system._find_vehicle_by_id(vehicle_id)
        if not vehicle:
            flash('Vehicle not found.', 'error')
            return redirect(url_for('vehicles'))
        
        if request.method == 'POST':
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            user_id = session.get('user_id')
            
            try:
                # Convert dates to DD-MM-YYYY format
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                start_formatted = start_dt.strftime('%d-%m-%Y')
                end_formatted = end_dt.strftime('%d-%m-%Y')
                
                period = RentalPeriod(start_formatted, end_formatted)
                
                # Process rental
                success = rental_system.rent_vehicles(vehicle_id, user_id, period)
                
                if success:
                    flash('Vehicle rented successfully!', 'success')
                    return redirect(url_for('rental_invoice', vehicle_id=vehicle_id))
                else:
                    flash('Rental failed. Vehicle may not be available.', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
        
        return render_template('rent_form.html', vehicle=vehicle)
    
    @app.route('/invoice/<vehicle_id>')
    @login_required
    def rental_invoice(vehicle_id):
        """Display rental invoice."""
        user_id = session.get('user_id')
        user = rental_system._find_renter_by_id(user_id)
        
        # Get user's current rentals
        user_rentals = user.get_current_rentals()
        
        # Find the rental for this vehicle
        vehicle_rental = None
        for rental in user_rentals:
            if rental['vehicle_id'] == vehicle_id:
                vehicle_rental = rental
                break
        
        if not vehicle_rental:
            flash('No rental record found.', 'error')
            return redirect(url_for('dashboard'))
        
        vehicle = rental_system._find_vehicle_by_id(vehicle_id)
        
        return render_template('invoice.html',
                             rental=vehicle_rental,
                             vehicle=vehicle,
                             user=user)
    
    @app.route('/return/<vehicle_id>', methods=['GET', 'POST'])
    @login_required
    def return_vehicle(vehicle_id):
        """Handle vehicle return with early return support."""
        user_id = session.get('user_id')
        user = rental_system._find_renter_by_id(user_id)
        
        # Find active rental
        current_rentals = user.get_current_rentals()
        vehicle_rental = None
        for rental in current_rentals:
            if rental['vehicle_id'] == vehicle_id:
                vehicle_rental = rental
                break
        
        if not vehicle_rental:
            flash('No active rental found for this vehicle.', 'error')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            try:
                # Get actual return date from form (for early return)
                return_date = request.form.get('return_date')
                
                if return_date:
                    # Early return - use actual return date
                    return_dt = datetime.strptime(return_date, '%Y-%m-%d')
                    actual_return = return_dt.strftime('%d-%m-%Y')
                    
                    # Create period with actual dates
                    actual_period = RentalPeriod(
                        vehicle_rental['start_date'],
                        actual_return,
                        allow_past_dates=True
                    )
                    
                    # Calculate actual days used
                    actual_days = actual_period.calculate_duration()
                    
                    # Check if returning early
                    original_period = RentalPeriod(
                        vehicle_rental['start_date'],
                        vehicle_rental['end_date'],
                        allow_past_dates=True
                    )
                    original_days = original_period.calculate_duration()
                    
                    is_early = actual_days < original_days
                else:
                    # Normal return on scheduled date
                    actual_return = vehicle_rental['end_date']
                    is_early = False
                    actual_period = RentalPeriod(
                        vehicle_rental['start_date'],
                        vehicle_rental['end_date'],
                        allow_past_dates=True
                    )
                
                # Process return
                success = rental_system.return_vehicles(vehicle_id, user_id, actual_period)
                
                if success:
                    if is_early:
                        flash(f'Vehicle returned early! Charged for actual {actual_days} days used.', 'success')
                    else:
                        flash('Vehicle returned successfully!', 'success')
                    return redirect(url_for('return_invoice', vehicle_id=vehicle_id))
                else:
                    flash('Return failed.', 'error')
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
        
        vehicle = rental_system._find_vehicle_by_id(vehicle_id)
        
        # Calculate if early return and potential refund
        today = datetime.now()
        end_date_obj = datetime.strptime(vehicle_rental['end_date'], '%d-%m-%Y')
        can_return_early = today < end_date_obj
        
        return render_template('return_form.html',
                             vehicle=vehicle,
                             rental=vehicle_rental,
                             can_return_early=can_return_early,
                             today=today.strftime('%Y-%m-%d'))
    
    
    @app.route('/return-invoice/<vehicle_id>')
    @login_required
    def return_invoice(vehicle_id):
        """Display return invoice with actual charges."""
        user_id = session.get('user_id')
        user_rentals = rental_system.get_rental_records_by_renter(user_id)
        
        # Find the latest completed rental for this vehicle
        vehicle_rentals = [r for r in user_rentals if r.get_vehicle_id() == vehicle_id and r.is_completed()]
        if not vehicle_rentals:
            flash('No completed rental record found.', 'error')
            return redirect(url_for('dashboard'))
        
        latest_rental = vehicle_rentals[-1]
        vehicle = rental_system._find_vehicle_by_id(vehicle_id)
        user = rental_system._find_renter_by_id(user_id)
        
        return render_template('return_invoice.html',
                             rental=latest_rental,
                             vehicle=vehicle,
                             user=user)
    
    @app.route('/history')
    @login_required
    def rental_history():
        """Display user's rental history."""
        user_id = session.get('user_id')
        user = rental_system._find_renter_by_id(user_id)
        
        # Get rental history from user object
        rentals = user.get_rental_history()
        
        return render_template('history.html', rentals=rentals)
    
    # ============ Staff Management Routes ============
    @app.route('/staff/users')
    @login_required
    @staff_required
    def staff_users():
        """Display all users (staff only)."""
        users = rental_system.get_renters()
        return render_template('staff_users.html', users=users)
    
    @app.route('/staff/users/add', methods=['GET', 'POST'])
    @login_required
    @staff_required
    def staff_add_user():
        """Add new user (staff only)."""
        if request.method == 'POST':
            user_type = request.form.get('user_type')
            user_id = request.form.get('user_id')
            name = request.form.get('name')
            contact = request.form.get('contact')
            password = request.form.get('password', 'password123')
            
            try:
                if user_type == 'Individual':
                    dob = request.form.get('dob')
                    license = request.form.get('license')
                    user = IndividualUser(user_id, name, contact, dob, license, password)
                elif user_type == 'Corporate':
                    company = request.form.get('company')
                    registration = request.form.get('registration')
                    address = request.form.get('address')
                    user = CorporateUser(user_id, name, contact, company, registration, address, password)
                else:
                    flash('Invalid user type.', 'error')
                    return redirect(url_for('staff_add_user'))
                
                rental_system.add_users(user)
                flash(f'User {name} added successfully!', 'success')
                return redirect(url_for('staff_users'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
        
        return render_template('staff_add_user.html')
    
    @app.route('/staff/users/delete/<user_id>')
    @login_required
    @staff_required
    def staff_delete_user(user_id):
        """Delete user (staff only)."""
        # Prevent self-deletion
        if user_id == session.get('user_id'):
            flash('Cannot delete your own account.', 'error')
            return redirect(url_for('staff_users'))
        
        users = rental_system.get_renters()
        user_to_delete = None
        for user in users:
            if user.get_renter_id() == user_id:
                user_to_delete = user
                break
        
        if user_to_delete:
            rental_system._VehicleRental__renters.remove(user_to_delete)
            rental_system.save_data()
            flash('User deleted successfully.', 'success')
        else:
            flash('User not found.', 'error')
        
        return redirect(url_for('staff_users'))
    
    @app.route('/staff/vehicles')
    @login_required
    @staff_required
    def staff_vehicles():
        """Display all vehicles (staff only)."""
        vehicles = rental_system.get_vehicles()
        return render_template('staff_vehicles.html', vehicles=vehicles)
    
    @app.route('/staff/vehicles/add', methods=['GET', 'POST'])
    @login_required
    @staff_required
    def staff_add_vehicle():
        """Add new vehicle (staff only)."""
        if request.method == 'POST':
            vehicle_type = request.form.get('vehicle_type')
            vehicle_id = request.form.get('vehicle_id')
            make = request.form.get('make')
            model = request.form.get('model')
            year = int(request.form.get('year'))
            daily_rate = float(request.form.get('daily_rate'))
            
            try:
                if vehicle_type == 'Car':
                    doors = int(request.form.get('doors'))
                    fuel = request.form.get('fuel')
                    transmission = request.form.get('transmission')
                    vehicle = Car(vehicle_id, make, model, year, daily_rate, doors, fuel, transmission)
                elif vehicle_type == 'Motorbike':
                    engine = int(request.form.get('engine'))
                    bike_type = request.form.get('bike_type')
                    has_abs = request.form.get('has_abs') == 'on'
                    vehicle = Motorbike(vehicle_id, make, model, year, daily_rate, engine, bike_type, has_abs)
                elif vehicle_type == 'Truck':
                    capacity = float(request.form.get('capacity'))
                    truck_type = request.form.get('truck_type')
                    has_lift = request.form.get('has_lift') == 'on'
                    vehicle = Truck(vehicle_id, make, model, year, daily_rate, capacity, truck_type, has_lift)
                else:
                    flash('Invalid vehicle type.', 'error')
                    return redirect(url_for('staff_add_vehicle'))
                
                rental_system.add_vehicles(vehicle)
                flash(f'Vehicle {make} {model} added successfully!', 'success')
                return redirect(url_for('staff_vehicles'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
        
        return render_template('staff_add_vehicle.html')
    
    @app.route('/staff/vehicles/delete/<vehicle_id>')
    @login_required
    @staff_required
    def staff_delete_vehicle(vehicle_id):
        """Delete vehicle (staff only)."""
        vehicle = rental_system._find_vehicle_by_id(vehicle_id)
        
        if vehicle:
            # Check if vehicle is currently rented
            if vehicle.is_currently_rented():
                flash('Cannot delete vehicle. It is currently rented.', 'error')
            else:
                rental_system._VehicleRental__vehicles.remove(vehicle)
                rental_system.save_data()
                flash('Vehicle deleted successfully.', 'success')
        else:
            flash('Vehicle not found.', 'error')
        
        return redirect(url_for('staff_vehicles'))
    
    @app.route('/staff/analytics')
    @login_required
    @staff_required
    def staff_analytics():
        """Display analytics (staff only)."""
        vehicles = rental_system.get_vehicles()
        records = rental_system.get_rental_records()
        
        # Calculate statistics
        vehicle_rental_counts = {}
        total_revenue = 0
        
        for record in records:
            vid = record.get_vehicle_id()
            vehicle_rental_counts[vid] = vehicle_rental_counts.get(vid, 0) + 1
            if record.is_completed():
                total_revenue += record.get_rental_cost()
        
        # Most/least rented
        if vehicle_rental_counts:
            most_rented_id = max(vehicle_rental_counts, key=vehicle_rental_counts.get)
            least_rented_id = min(vehicle_rental_counts, key=vehicle_rental_counts.get)
            most_rented = rental_system._find_vehicle_by_id(most_rented_id)
            least_rented = rental_system._find_vehicle_by_id(least_rented_id)
        else:
            most_rented = least_rented = None
        
        return render_template('staff_analytics.html',
                             total_revenue=total_revenue,
                             total_rentals=len(records),
                             most_rented=most_rented,
                             least_rented=least_rented,
                             vehicle_counts=vehicle_rental_counts)
    
    @app.route('/staff/history')
    @login_required
    @staff_required
    def staff_history():
        """Display all rental history (staff only)."""
        records = rental_system.get_rental_records()
        return render_template('staff_history.html', records=records)