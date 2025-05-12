# Courier Management System - Client Review Version

This is a **customer-facing portal** for the Courier Management System, prepared specifically for client review. This version focuses only on the customer experience and does not include admin functionality.

## Features Available for Review

- User registration and login
- Package sending and tracking
- Price calculation
- Delivery status updates
- User profile management

## How to Test

1. Create a new account (Register)
2. Log in with your credentials
3. Try sending a package with different weight options
4. Track your package status
5. Update your profile information

## Feedback

We welcome your feedback on:
- User interface and experience
- Functionality and features
- Any issues or bugs encountered
- Suggestions for improvements

Please share your thoughts through the provided feedback channels.

## Technical Details

This is a Django-based web application with:
- Bootstrap for responsive design
- SQLite database for data storage
- User authentication system

*Note: This is a review version with the admin panel disabled. The full version will include admin functionality for managing couriers, packages, and services.*

## Features

### For Customers
- **Home Page**: Overview of services and company information
- **Order Service**: Place new shipping orders easily
- **Order Tracking**: Track your packages with order IDs or tracking numbers
- **Product Information**: View available shipping services
- **Contact Form**: Get in touch with customer service

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Django 3.2 or higher
- Other dependencies listed in requirements.txt

### Installation

1. Clone the repository:
```
git clone https://github.com/YourUsername/Courier-Management-System.git
cd Courier-Management-System
```

2. Create a virtual environment and activate it:
```
python -m venv venv
# For Windows
venv\Scripts\activate
# For macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Apply migrations:
```
python manage.py migrate
```

5. Create a superuser (for testing purposes):
```
python create_superuser.py
```
*Note: By default, this creates an admin user with username: admin, password: admin@123456. You can customize these by setting environment variables. See [SUPERUSER_SETUP.md](SUPERUSER_SETUP.md) for details.*

6. Run the development server:
```
python manage.py runserver
```

7. Access the site at http://127.0.0.1:8000/

## Customer Usage Guide

1. **Creating an Account**: Click on "Sign Up" to create a new customer account
2. **Placing an Order**: Navigate to "Order" and fill out the shipping form
3. **Tracking a Package**: Use the "Tracker" page with your order ID to check status

## Technical Notes

- This repository contains only the customer-facing components
- The admin panel will be provided separately
- Database: SQLite (development), can be configured for PostgreSQL in production
- Static files are included for ease of review

## Contact

For any questions regarding this review, please contact us at your.email@example.com

## Live Demo

This project is deployed on Render: [Courier Management System](https://courier-management-system.onrender.com)

## Deployment

This project is configured for deployment on Render with PostgreSQL database support.

### Render Deployment

For detailed instructions on deploying this project to Render with PostgreSQL, see:
- [DEPLOY_TO_RENDER.md](DEPLOY_TO_RENDER.md)

The deployment configuration includes:
- Web service configuration in render.yaml
- PostgreSQL database setup
- Environment variables
- Static file serving with whitenoise
- Database migration instructions

## Technologies Used

- Django 3.2.18
- SQLite (local development)
- PostgreSQL (production)
- Bootstrap 4
- django-crispy-forms
- whitenoise for static files
- gunicorn (production server)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
