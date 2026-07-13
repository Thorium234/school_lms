# 📚 School Library Management System (School LMS)

A comprehensive, full-stack web application designed to streamline library operations, automate book tracking, and manage student/staff borrowing activities seamlessly.

---

## 🛠️ Tech Stack & Architecture

This project is built using a robust Python backend paired with a dynamic, responsive front-end interface:

*   **Backend Framework:** Python (Django framework implied by `manage.py` and `db.sqlite3`)
*   **Database:** SQLite3 (Development default)
*   **Frontend Languages:** JavaScript (31.2%), HTML (30.2%), CSS (21.8%)

---

## 🚀 Key Features

### 👤 User Management (`/users`)
*   **Role-Based Access Control:** Separate dashboards and permissions for Librarians and Students.
*   **Authentication System:** Secure user registration, login, and profile management.

### 📖 Library Core Engine (`/library`)
*   **Catalog Management:** Add, update, and remove books with details like ISBN, Author, and Genre.
*   **Digital Ledger:** Track real-time inventory, available copies, and shelf locations.
*   **Issue & Return Tracking:** Automate the borrowing pipeline with due-date calculations and fine tracking.

### 🎨 Interface & Assets (`/static`, `/templates`)
*   **Modern UI:** Clean templates built with interactive JavaScript components and styled CSS layout grids.
*   **Responsive Design:** Fully optimized for both desktop monitors and tablet views.

---

## 📂 Project Structure

```text
school_lms/
│
├── school/             # Core project configuration files
├── library/            # Book cataloging, issuing, and transactional logic
├── users/              # User profiles, authentication, and permission states
├── templates/          # Global HTML templates and layout definitions
├── static/             # Raw frontend assets (CSS, JS, Images)
├── staticfiles/        # Compiled/collected static assets for deployment
├── db.sqlite3          # Local development database
├── manage.py           # Django administrative command-line utility
└── requirements.txt    # Project dependencies and package versions
```

---

## ⚙️ Quick Start Guide

Follow these steps to get a local copy of the project up and running.

### 1. Clone the Repository
```bash
git clone https://github.com/Thorium234/school_lms.git
cd school_lms
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Migrations
Initialize your local database schema:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create an Administrative Account
Generate a superuser login to access the backend admin panel:
```bash
python manage.py createsuperuser
```

### 6. Run the Application
Start the local development server:
```bash
python manage.py runserver
```
Once started, navigate to `http://127.0.0` in your web browser to view the application.

---

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
