# Vehicle Rental Web Application

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initial Data (Included)
The application comes with pre-loaded data in `data/rental_data.pkl`:
- **5 Users**: 2 Individual, 2 Corporate, 1 Staff (Admin)
- **10 Vehicles**: 4 Cars, 3 Motorbikes, 3 Trucks

**Default Login Credentials:**
- Individual: I001 / password123
- Corporate: C001 / password123
- Staff: S001 / password123

### 3. Run the Application
```bash
python run.py
```

### 4. Access the System
Open your browser and go to: **http://127.0.0.1:5000**

## Default Login Accounts

| User Type | User ID | Password | Description |
|-----------|---------|----------|-------------|
| Individual | I001 | password123 | Regular customer |
| Corporate | C001 | password123 | Corporate customer (15% discount) |
| Staff | S001 | password123 | Administrator access |

## Features

### For Individual & Corporate Users:
- ✅ Browse and search vehicles (by type, brand, price)
- ✅ View vehicle details with **availability calendar** 
- ✅ Rent vehicles
- ✅ Return vehicles **early return supported**
- ✅ View rental history
- ✅ Generate invoices
- ✅ Automatic discount calculation

### For Staff Users:
- ✅ Manage users (add/remove)
- ✅ Manage vehicles (add/remove)
- ✅ View all rental history
- ✅ Analytics dashboard (revenue, most/least rented)

## User Discounts

- **Individual Users**: 10% discount for rentals ≥ 7 days
- **Corporate Users**: 15% discount on all rentals
- **Staff Users**: No discount (administrative accounts)

## Technology Stack

- **Backend**: Flask 3.0.0
- **Frontend**: HTML5, CSS3, JavaScript
- **Data Storage**: Pickle
- **Template Engine**: Jinja2

## Project Status

✅ **Step 1 Complete**: Model Layer
✅ **Step 2 Complete**: Web Application (Controller + View)
✅ **Step 3**: Testing (Unit + Integration)

## Development Notes

- All data is automatically saved to `data/rental_data.pkl`
- Session management for user authentication
- Role-based access control (Individual/Corporate/Staff)
- Responsive design for different screen sizes
- Print-friendly invoice layout

## Next Steps

1. Run unit tests (tests/test_models.py)
2. Run integration tests (tests/test_integration.py)