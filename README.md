# Smart Society Management System

Minimal Django MVP for an apartment/society management workflow.

## Features

- Resident registration and login
- Resident complaint submission and complaint history
- Staff portal for complaint updates and notice management
- Society notices visible to all logged-in residents
- Complaint search, date filtering, and status filtering
- Dashboard with total, pending, and resolved complaint counts

## Default Admin

- Email: `admin@society.com`
- Password: `admin123`

## Portal Routes

- Resident portal: `/login/`, `/register/`, `/resident/dashboard/`
- Staff portal: `/staff/login/`, `/staff/register/`, `/staff/dashboard/`

## Local Setup

1. Create and activate the virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Create the database tables:
```powershell
python manage.py makemigrations
python manage.py migrate
```

4. Create an admin account for staff access:
```powershell
python manage.py createsuperuser
```

The project also seeds a default admin account automatically after migrations.

5. Run the app:
```powershell
python manage.py runserver
```

## Usage

- Residents register through the app and can raise complaints.
- Admin users log in with a superuser or staff account and can update complaint status and post notices.