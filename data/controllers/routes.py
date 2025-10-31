"""
Routes Controller for Vehicle Rental Application.

Handles all HTTP routes and business logic for the web application.
"""

from flask import render_template, request, redirect, url_for, session, flash
from functools import wraps
from werkzeug.utils import secure_filename
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

    # ============ Custom Jinja2 Filters ============
    def format_datetime(date_string):
        """
        Format datetime string to uniform display format: DD-MM-YYYY

        Handles two input formats:
        - "YYYY-MM-DD HH:MM:SS" (from created_at)
        - "DD-MM-YYYY" (from start_date, end_date, actual_return_date)
        """
        if not date_string:
            return "N/A"

        try:
            # Check if it's a full datetime string (YYYY-MM-DD HH:MM:SS)
            if len(date_string) > 10 and ' ' in date_string:
                # Parse "YYYY-MM-DD HH:MM:SS" format and extract only the date
                dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
                return dt.strftime("%d-%m-%Y")
            else:
                # It's already in "DD-MM-YYYY" format
                return date_string
        except:
            # If parsing fails, return original string
            return date_string

    # Register the custom filter
    app.jinja_env.filters['format_datetime'] = format_datetime

    # ============ Helper Functions ============
    def allowed_file(filename):
        """Check if file has allowed extension."""
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def handle_vehicle_image_upload(vehicle_id):
        """Handle vehicle image upload and return filename."""
        if 'vehicle_image' not in request.files:
            return 'default.jpg'

        file = request.files['vehicle_image']
        if file.filename == '':
            return 'default.jpg'

        if file and allowed_file(file.filename):
            # Use vehicle_id as filename with original extension
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{vehicle_id}.{file_ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return filename

        return 'default.jpg'

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

    def non_staff_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_type' in session and session['user_type'] == 'Staff':
                flash('Staff cannot rent or return vehicles.', 'error')
                # Get the vehicle_id from kwargs if available
                vehicle_id = kwargs.get('vehicle_id')
                if vehicle_id:
                    return redirect(url_for('vehicle_detail', vehicle_id=vehicle_id))
                return redirect(url_for('vehicles'))
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

        # Get rental records for this vehicle to show in calendar
        rental_records = rental_system.get_rental_records_by_vehicle(vehicle_id)

        return render_template('vehicle_detail.html',
                             vehicle=vehicle,
                             rental_records=rental_records)
    
    # ============ Rental Routes ============
    @app.route('/rent/<vehicle_id>', methods=['GET', 'POST'])
    @login_required
    @non_staff_required
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

        # Get rental periods to disable rented dates in the form
        rental_periods = vehicle.get_rental_periods()

        return render_template('rent_form.html',
                             vehicle=vehicle,
                             rental_periods=rental_periods)
    
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
    @non_staff_required
    def return_vehicle(vehicle_id):
        """Handle vehicle return with early/normal/overdue support."""
        user_id = session.get('user_id')

        # Find active rental record
        active_record = None
        for record in rental_system.get_rental_records():
            if (record.get_vehicle_id() == vehicle_id and
                record.get_renter_id() == user_id and
                record.is_active()):
                active_record = record
                break

        if not active_record:
            flash('No active rental found for this vehicle.', 'error')
            return redirect(url_for('dashboard'))

        vehicle = rental_system._find_vehicle_by_id(vehicle_id)

        if request.method == 'POST':
            return_date = request.form.get('return_date')

            try:
                # Convert date format from YYYY-MM-DD to DD-MM-YYYY
                return_dt = datetime.strptime(return_date, '%Y-%m-%d')
                return_formatted = return_dt.strftime('%d-%m-%Y')

                # Process return using new method
                result = rental_system.return_vehicle_with_date(
                    vehicle_id,
                    user_id,
                    return_formatted
                )

                if result['success']:
                    # Show confirmation page with details
                    return render_template('return_confirmation.html',
                                         result=result,
                                         vehicle=vehicle)
                else:
                    flash(result.get('error', 'Return failed'), 'error')

            except Exception as e:
                flash(f'Error: {str(e)}', 'error')

        # Calculate return context
        today = datetime.now()
        scheduled_end = datetime.strptime(active_record.get_end_date(), '%d-%m-%Y')

        return render_template('return_form.html',
                             vehicle=vehicle,
                             rental_record=active_record,
                             today=today.strftime('%Y-%m-%d'),
                             scheduled_end_date=scheduled_end.strftime('%Y-%m-%d'))
    


    @app.route('/history')
    @login_required
    def rental_history():
        """Display user's rental history."""
        user_id = session.get('user_id')

        # Get rental records from rental system (includes all return information)
        rental_records = rental_system.get_rental_records_by_renter(user_id)

        return render_template('history.html', rental_records=rental_records)

    @app.route('/history/invoice/<record_id>')
    @login_required
    def user_rental_invoice(record_id):
        """Display rental invoice for user's own record."""
        user_id = session.get('user_id')

        # Find the rental record
        record = None
        for r in rental_system.get_rental_records():
            if r.get_record_id() == record_id and r.get_renter_id() == user_id:
                record = r
                break

        if not record:
            flash('Rental record not found or access denied.', 'error')
            return redirect(url_for('rental_history'))

        # Get vehicle and renter information
        vehicle = rental_system._find_vehicle_by_id(record.get_vehicle_id())
        user = rental_system._find_renter_by_id(user_id)

        if not vehicle or not user:
            flash('Vehicle or user information not found.', 'error')
            return redirect(url_for('rental_history'))

        # Prepare rental data
        rental = {
            'vehicle_id': record.get_vehicle_id(),
            'start_date': record.get_start_date(),
            'end_date': record.get_end_date(),
            'duration': record.calculate_duration(),
            'cost': record.get_rental_cost(),
            'status': record.get_status()
        }

        return render_template('invoice.html',
                             rental=rental,
                             vehicle=vehicle,
                             user=user)

    @app.route('/history/return_invoice/<record_id>')
    @login_required
    def user_return_invoice(record_id):
        """Display return confirmation invoice for user's own completed record."""
        user_id = session.get('user_id')

        # Find the rental record
        record = None
        for r in rental_system.get_rental_records():
            if r.get_record_id() == record_id and r.get_renter_id() == user_id:
                record = r
                break

        if not record:
            flash('Rental record not found or access denied.', 'error')
            return redirect(url_for('rental_history'))

        if record.get_status() != 'completed':
            flash('This rental has not been completed yet.', 'error')
            return redirect(url_for('rental_history'))

        # Get vehicle information
        vehicle = rental_system._find_vehicle_by_id(record.get_vehicle_id())

        if not vehicle:
            flash('Vehicle information not found.', 'error')
            return redirect(url_for('rental_history'))

        # Prepare result data (similar to return_vehicle route)
        scheduled_days = record.calculate_duration()
        actual_days = record.calculate_actual_duration()
        original_cost = record.get_rental_cost()
        final_cost = record.get_final_cost() if record.get_final_cost() else original_cost

        # Calculate refund or penalty
        refund = 0
        penalty = 0
        if record.get_return_type() == 'early':
            refund = original_cost - final_cost
        elif record.get_return_type() == 'overdue':
            penalty = final_cost - original_cost

        # Prepare message
        if record.get_return_type() == 'early':
            message = f"Vehicle returned {scheduled_days - actual_days} day(s) early. Refund issued."
        elif record.get_return_type() == 'overdue':
            message = f"Vehicle returned {actual_days - scheduled_days} day(s) late. Overdue penalty applied."
        else:
            message = "Vehicle returned on time."

        result = {
            'success': True,
            'record': record,
            'return_type': record.get_return_type() if record.get_return_type() else 'normal',
            'scheduled_end_date': record.get_end_date(),
            'actual_return_date': record.get_actual_return_date(),
            'scheduled_days': scheduled_days,
            'actual_days': actual_days,
            'original_cost': original_cost,
            'final_cost': final_cost,
            'refund': refund,
            'penalty': penalty,
            'message': message
        }

        return render_template('return_confirmation.html',
                             result=result,
                             vehicle=vehicle)

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

            # Handle image upload
            image_filename = handle_vehicle_image_upload(vehicle_id)

            try:
                if vehicle_type == 'Car':
                    doors = int(request.form.get('doors'))
                    fuel = request.form.get('fuel')
                    transmission = request.form.get('transmission')
                    vehicle = Car(vehicle_id, make, model, year, daily_rate, doors, fuel, transmission, image_filename)
                elif vehicle_type == 'Motorbike':
                    engine = int(request.form.get('engine'))
                    bike_type = request.form.get('bike_type')
                    has_abs = request.form.get('has_abs') == 'on'
                    vehicle = Motorbike(vehicle_id, make, model, year, daily_rate, engine, bike_type, has_abs, image_filename)
                elif vehicle_type == 'Truck':
                    capacity = float(request.form.get('capacity'))
                    truck_type = request.form.get('truck_type')
                    has_lift = request.form.get('has_lift') == 'on'
                    vehicle = Truck(vehicle_id, make, model, year, daily_rate, capacity, truck_type, has_lift, image_filename)
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
        users = rental_system.get_renters()

        # Calculate statistics
        vehicle_rental_counts = {}
        vehicle_revenue = {}
        total_revenue = 0
        total_days = 0
        completed_rentals = 0

        # Revenue by vehicle type
        revenue_by_vehicle_type = {'Car': 0, 'Motorbike': 0, 'Truck': 0}
        rentals_by_vehicle_type = {'Car': 0, 'Motorbike': 0, 'Truck': 0}

        # Revenue by user type
        revenue_by_user_type = {'Individual': 0, 'Corporate': 0, 'Staff': 0}
        rentals_by_user_type = {'Individual': 0, 'Corporate': 0, 'Staff': 0}

        for record in records:
            vid = record.get_vehicle_id()
            vehicle = rental_system._find_vehicle_by_id(vid)
            user = rental_system._find_renter_by_id(record.get_renter_id())

            # Count rentals per vehicle
            vehicle_rental_counts[vid] = vehicle_rental_counts.get(vid, 0) + 1

            if record.is_completed():
                # Use final cost if available (after return), otherwise use rental cost
                cost = record.get_final_cost() if record.get_final_cost() else record.get_rental_cost()
                total_revenue += cost

                # Track revenue per vehicle
                if vid not in vehicle_revenue:
                    vehicle_revenue[vid] = 0
                vehicle_revenue[vid] += cost

                # Use actual duration if available, otherwise use scheduled duration
                if record.get_actual_return_date():
                    total_days += record.calculate_actual_duration()
                else:
                    total_days += record.calculate_duration()

                completed_rentals += 1

                # Revenue by vehicle type
                if vehicle:
                    v_type = vehicle.get_vehicle_type()
                    revenue_by_vehicle_type[v_type] += cost
                    rentals_by_vehicle_type[v_type] += 1

                # Revenue by user type
                if user:
                    u_type = user.get_user_type()
                    revenue_by_user_type[u_type] += cost
                    rentals_by_user_type[u_type] += 1

        # Calculate average revenue per rental
        avg_revenue = total_revenue / completed_rentals if completed_rentals > 0 else 0

        # Calculate average rental duration
        avg_days = total_days / completed_rentals if completed_rentals > 0 else 0

        # Top 5 most rented vehicles
        top_5_rented = sorted(vehicle_rental_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_5_vehicles = [(rental_system._find_vehicle_by_id(vid), count) for vid, count in top_5_rented]

        # Bottom 5 least rented vehicles
        bottom_5_rented = sorted(vehicle_rental_counts.items(), key=lambda x: x[1])[:5]
        bottom_5_vehicles = [(rental_system._find_vehicle_by_id(vid), count) for vid, count in bottom_5_rented]

        # Top 5 revenue generating vehicles
        top_5_revenue = sorted(vehicle_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
        top_5_revenue_vehicles = [(rental_system._find_vehicle_by_id(vid), revenue) for vid, revenue in top_5_revenue]

        # Most/least rented (overall)
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
                             completed_rentals=completed_rentals,
                             avg_revenue=avg_revenue,
                             avg_days=avg_days,
                             most_rented=most_rented,
                             least_rented=least_rented,
                             vehicle_counts=vehicle_rental_counts,
                             top_5_vehicles=top_5_vehicles,
                             bottom_5_vehicles=bottom_5_vehicles,
                             top_5_revenue_vehicles=top_5_revenue_vehicles,
                             revenue_by_vehicle_type=revenue_by_vehicle_type,
                             rentals_by_vehicle_type=rentals_by_vehicle_type,
                             revenue_by_user_type=revenue_by_user_type,
                             rentals_by_user_type=rentals_by_user_type,
                             records=records,
                             renters=users)
    
    @app.route('/staff/history')
    @login_required
    @staff_required
    def staff_history():
        """Display all rental history (staff only)."""
        records = rental_system.get_rental_records()
        return render_template('staff_history.html', records=records)

    @app.route('/staff/invoice/<record_id>')
    @login_required
    @staff_required
    def staff_rental_invoice(record_id):
        """Display rental invoice for any record (staff only)."""
        # Find the rental record
        record = None
        for r in rental_system.get_rental_records():
            if r.get_record_id() == record_id:
                record = r
                break

        if not record:
            flash('Rental record not found.', 'error')
            return redirect(url_for('staff_history'))

        # Get vehicle and renter information
        vehicle = rental_system._find_vehicle_by_id(record.get_vehicle_id())
        user = rental_system._find_renter_by_id(record.get_renter_id())

        if not vehicle or not user:
            flash('Vehicle or renter information not found.', 'error')
            return redirect(url_for('staff_history'))

        # Prepare rental data
        rental = {
            'vehicle_id': record.get_vehicle_id(),
            'start_date': record.get_start_date(),
            'end_date': record.get_end_date(),
            'duration': record.calculate_duration(),
            'cost': record.get_rental_cost(),
            'status': record.get_status()
        }

        return render_template('invoice.html',
                             rental=rental,
                             vehicle=vehicle,
                             user=user)

    @app.route('/staff/return_invoice/<record_id>')
    @login_required
    @staff_required
    def staff_return_invoice(record_id):
        """Display return confirmation invoice for any completed record (staff only)."""
        # Find the rental record
        record = None
        for r in rental_system.get_rental_records():
            if r.get_record_id() == record_id:
                record = r
                break

        if not record:
            flash('Rental record not found.', 'error')
            return redirect(url_for('staff_history'))

        if record.get_status() != 'completed':
            flash('This rental has not been completed yet.', 'error')
            return redirect(url_for('staff_history'))

        # Get vehicle information
        vehicle = rental_system._find_vehicle_by_id(record.get_vehicle_id())

        if not vehicle:
            flash('Vehicle information not found.', 'error')
            return redirect(url_for('staff_history'))

        # Prepare result data (similar to return_vehicle route)
        scheduled_days = record.calculate_duration()
        actual_days = record.calculate_actual_duration()
        original_cost = record.get_rental_cost()
        final_cost = record.get_final_cost() if record.get_final_cost() else original_cost

        # Calculate refund or penalty
        refund = 0
        penalty = 0
        if record.get_return_type() == 'early':
            refund = original_cost - final_cost
        elif record.get_return_type() == 'overdue':
            penalty = final_cost - original_cost

        # Prepare message
        if record.get_return_type() == 'early':
            message = f"Vehicle returned {scheduled_days - actual_days} day(s) early. Refund issued."
        elif record.get_return_type() == 'overdue':
            message = f"Vehicle returned {actual_days - scheduled_days} day(s) late. Overdue penalty applied."
        else:
            message = "Vehicle returned on time."

        result = {
            'success': True,
            'record': record,
            'return_type': record.get_return_type() if record.get_return_type() else 'normal',
            'scheduled_end_date': record.get_end_date(),
            'actual_return_date': record.get_actual_return_date(),
            'scheduled_days': scheduled_days,
            'actual_days': actual_days,
            'original_cost': original_cost,
            'final_cost': final_cost,
            'refund': refund,
            'penalty': penalty,
            'message': message
        }

        return render_template('return_confirmation.html',
                             result=result,
                             vehicle=vehicle)