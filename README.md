# 🎬 Movie Booking System

A backend-driven movie ticket booking application that enables users to browse movies, select showtimes, reserve seats, and manage bookings. The system is designed using a layered architecture to ensure modularity, scalability, and data integrity.

## 📌 Features

User Authentication
Secure registration and login system
Browse movies
View available showtimes
Seat Reservation
Dynamic seat selection
Prevention of double booking
Booking Management
Create, view, and cancel bookings
Payment Processing
Booking confirmation via SMTP (with fallback simulation)
Revenue tracking and booking analytics
Popular movies and recent activity insights

## 🏗️ System Architecture

The system follows a three-tier layered architecture:

### Frontend Layer: Tkinter UI

- Login / Signup
- Browse movies
- Select shows / seats
- Booking and payment
- View booking history
- Manager reports

### Database Design

Normalized relational database schema
Key tables:

- users
- movies
- shows
- theatres
- screens
- bookings
- booking_seats
- payments

### Backend Layer: Python

- Auth
- Movie
- Booking
- Payment
- Manager Report

## 🚀 Setup Instructions

```bash
pip install -r requirements.txt
python main.py
pytest tests/
```

## 📎 Notes

Static movie data used to focus on backend architecture
Email service supports real SMTP + fallback simulation

## 👥 Contributors

Allison Berkeland
Deborah Tinoco
Shivranjini Pandey
Tanushree Soni
