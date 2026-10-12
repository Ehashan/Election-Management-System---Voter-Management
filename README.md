# EMS - Voter Management System

A robust and secure Election Management System (EMS) designed for voter registration and management. This system uses modern web technologies to handle voter data efficiently, integrating face recognition capabilities for identity verification.

## 🚀 Features

- **Voter Registration:** Comprehensive registration form capturing essential details (NIC, DoB, District, etc.).
- **Facial Recognition Support:** Integrates webcam capabilities directly into the browser to capture and store voter photos for verification.
- **Secure Configuration:** Uses environment variables to securely store sensitive data such as secret keys and database URIs.
- **Dual Database Architecture:** 
  - **SQLite:** For local rapid development and default Django auth models.
  - **MongoDB:** Integrated for scalable, document-oriented storage of complex voter records and analytics.
- **Admin Dashboard:** Built-in Django admin interface for managing records.

## 🛠️ Technology Stack

- **Backend:** Python, Django
- **Database:** SQLite (default), MongoDB (pymongo)
- **Image Processing:** Pillow
- **Frontend:** HTML5, Vanilla CSS, JavaScript (MediaDevices API for webcam)
- **Environment Management:** python-dotenv

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- MongoDB instance (Local or Atlas)

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd EMS-Voter Management
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your_secret_key_here
DEBUG=True
MONGO_URI=your_mongodb_connection_string
MONGO_DB_NAME=Election_Management_System
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
*(If you are using the existing database, the default admin login is `Admin` / `admin123`)*

### 7. Run the Development Server
```bash
python manage.py runserver
```
Navigate to `http://localhost:8000` in your web browser.

## 📁 Project Structure

- `ems_project/`: Main Django project configuration settings.
- `voters/`: Core app handling voter registration and models.
- `templates/`: HTML templates (including `voter_registration.html` for face capture).
- `static/`: Static assets (CSS, JS, images).
- `media/`: Uploaded files and images.

## 🔒 Security
- `.env` and `.venv` are ignored via `.gitignore` to prevent secret leaks.
- Cross-Site Request Forgery (CSRF) protection is enabled on all forms.

---
*Developed for the Election Management System project.*
