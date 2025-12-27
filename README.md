# 🏋️ Gym Management System

A **full-stack Gym Management System** built to handle real gym workflows like **member management, smart renewals, QR-based attendance, grace periods, and archival**.

This project is designed with **real gym owner logic**, not toy CRUD.

---

## 🚀 Features

### 👤 Member Management

* Add, edit, archive (soft delete), restore, and permanently delete members
* Active vs Archived members separation
* Search & filter members by status (Active / Grace / Expired)

### 🔁 Smart Membership Renewal (Business Logic)

* Configurable **grace period**
* Balanced renewal logic:

  * Pays within grace → extends from old expiry
  * Pays after grace → renewal starts from grace end
  * Large gap → fresh cycle (no unfair extension)
* Prevents both **owner loss** and **member confusion**

### 📆 Attendance System (QR Based)

* Members mark attendance using **QR scan + last 4 digits**
* Time-restricted attendance window (e.g., 5 AM – 11 PM)
* Prevents duplicate attendance for the same day
* Attendance stored per date

### 📊 Attendance Calendar Support

* Backend API provides:

  * Joining date
  * All attendance dates
* Enables frontend calendar coloring:

  * 🟢 Present
  * 🔴 Absent
  * ⚪ Pre-Join

### 📈 Dashboard Summary

* Active, Grace, Expired member counts
* Today’s visits
* Upcoming expiries

---

## 🧠 Tech Stack

### Backend

* **Python**
* **Django**
* **Django REST Framework**
* **JWT Authentication**
* SQLite (development)

### Frontend

* **React**
* **Axios**
* Tailwind CSS (UI layer)

---

## 🔐 Authentication

* JWT-based authentication
* Protected owner routes
* Public QR attendance endpoint (controlled via config)

---

## 📁 Project Structure

```
gym_backend/
│
├── core/
│   ├── models.py        # Member, Attendance, GymConfig
│   ├── views.py         # All APIs
│   ├── serializers.py
│   ├── urls.py
│   └── utils.py         # Status & business logic
│
├── gym_backend/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
└── README.md
```

---

## ▶️ How to Run Locally

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Rahulcherukuwada28/Gym_management-system.git
cd gym_backend
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Migrations

```bash
python manage.py migrate
```

### 5️⃣ Start Server

```bash
python manage.py runserver
```

Backend runs at:

```
http://127.0.0.1:8000/
```

---

## 🔌 Important API Endpoints

| Endpoint                                | Method | Description              |
| --------------------------------------- | ------ | ------------------------ |
| `/api/members/`                         | GET    | List active members      |
| `/api/members/`                         | POST   | Add member               |
| `/api/members/{id}/`                    | DELETE | Archive member           |
| `/api/members/{id}/renew/`              | POST   | Renew membership         |
| `/api/members/archived/`                | GET    | View archived members    |
| `/api/members/{id}/attendance-history/` | GET    | Attendance calendar data |
| `/api/attendance/mark/`                 | POST   | QR attendance            |

---

## ⚙️ Business Rules Implemented

* Grace days are **not free**, but **not wasted**
* Attendance allowed only within configured time
* No duplicate attendance per day
* Backend controls all critical business logic (frontend is dumb)

---

## 🧪 Status

✔ Backend logic complete
✔ Attendance + renewal validated
✔ Git repository clean and production-ready

---

## 👨‍💻 Author

**Rahul Cherukuvada**
Python Full-Stack Developer

---

