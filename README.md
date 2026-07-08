# mobile-shop-management-system
Python Tkinter based Mobile Shop Management System with MySQL
# 📱 Mobile Shop Management System

A desktop application built with **Python (Tkinter)** and **MySQL** for managing a mobile phone shop — including inventory, customers, suppliers, sales, and reporting, with a secure login system and a public customer-facing catalog.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)
![MySQL](https://img.shields.io/badge/Database-MySQL-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 🔐 Authentication
- Secure **Sign Up / Login / Logout** with salted SHA-256 password hashing
- **Forgot Password** recovery flow using a security question & answer
- **Guest / Customer Mode** — browse available stock without logging in
<img width="322" height="263" alt="Screenshot 2026-07-08 141746" src="https://github.com/user-attachments/assets/65889ff8-b32b-44fc-9aca-9f5c42e1782d" />

### 📊 Admin Dashboard
- Live stats: total products, total units in stock, total sales, low-stock alerts
- Real-time clock display
<img width="590" height="274" alt="Screenshot 2026-07-08 141840" src="https://github.com/user-attachments/assets/508919f1-62e4-4516-8d92-0fd066e970b0" />

### 📦 Product Management
- Add, update, delete, and search phones (brand, model, price, quantity)
- Sortable inventory table
- Automatic low-stock and out-of-stock highlighting
 <img width="568" height="284" alt="Screenshot 2026-07-08 141902" src="https://github.com/user-attachments/assets/2d79b220-0439-469e-aafd-b075acf31431" />

### 👥 Customer & 🚚 Supplier Management
- Full CRUD (Create, Read, Update, Delete) for customers and suppliers
- Reusable generic CRUD builder for consistent UI across modules
<img width="592" height="261" alt="Screenshot 2026-07-08 141925" src="https://github.com/user-attachments/assets/e17c6b4c-4edb-4b26-a20a-c784301b4365" />



### 💰 Sales Management
- Record sales against existing inventory
- Auto-calculates total amount and deducts sold quantity from stock
- Prevents overselling beyond available stock
- <img width="608" height="263" alt="Screenshot 2026-07-08 142041" src="https://github.com/user-attachments/assets/65152daf-725e-4d58-ac1b-4fd810f0917c" />


### 🛍️ Customer Catalog (Public View)
- Read-only, searchable product catalog for customers
- Stock availability shown with color-coded status (In Stock / Low / Out of Stock)

### 📈 Reports
- Inventory summary (models, units, total value)
- Sales summary (transactions, units sold, revenue)
- Top 5 best-selling products
- <img width="596" height="270" alt="Screenshot 2026-07-08 142100" src="https://github.com/user-attachments/assets/7be31ab1-9be6-4666-a996-33bf10eb7842" />


### ⚙️ Settings
- Configure low-stock threshold and currency symbol (session-based)


## 🖥️ Tech Stack

| Component  | Technology              |
|------------|--------------------------|
| Language   | Python 3                |
| GUI        | Tkinter + ttk            |
| Database   | MySQL                    |
| Security   | `hashlib` (SHA-256 + salt) |

## 📂 Project Structure

```
mobile-shop-management-system/
│
├── main.py            # Main application (UI, logic, pages)
├── database.py        # Database connection (db, cursor)
├── create_tables.sql  # SQL script to create required tables
└── README.md

> **Note:** Make sure you have a `database.py` file that exposes a MySQL connection object `db` and a cursor `cursor`, e.g.:
> ```python
> import mysql.connector
> db = mysql.connector.connect(
>     host="localhost",
>     user="root",
>     password="yourpassword",
>     database="mobile_shop"
> )
> cursor = db.cursor()
> ```

## 🗄️ Database Schema

The app expects the following MySQL tables (see `create_tables.sql`):

- **users** — `id, username, password_hash, email, security_question, security_answer_hash`
- **phones** — `id, brand, model, price, quantity`
- **customers** — `id, name, phone, email, address`
- **suppliers** — `id, company_name, phone, email, address`
- **sales** — `id, customer_name, product_name, quantity, total_amount, sale_date`
<img width="445" height="240" alt="Screenshot 2026-07-08 225927" src="https://github.com/user-attachments/assets/f50f2942-4b01-40c8-9f61-34e64289e928" />


## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- MySQL Server
- `mysql-connector-python` package

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/mobile-shop-management-system.git
cd mobile-shop-management-system

# Install dependencies
pip install mysql-connector-python

# Set up the database
mysql -u root -p < create_tables.sql

# Run the app
python main.py
```

## 🎨 Theme

The UI uses a customizable color palette (`COLORS` dictionary) that can be easily tweaked to change the app's look — for example, switching to a Dark Navy & Gold theme.



## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to fork the repo and submit a pull request.


## 📄 License

This project is licensed under the MIT License.


## 👤 Author

**Shakeel** —
Built as part of the Technify AI/Development Internship (Cohort IV).
