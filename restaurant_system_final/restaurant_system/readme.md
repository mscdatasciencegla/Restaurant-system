# Restaurant Management System

# Project Info
- **Course:** OOP Final Project
- **Instructor:** Mohamed Abu Obaida
- **Project:** Restaurant Management System
- **Team Size:** 2 students

# Team Members
- Student 1 (Models, OOP, Business Logic, File Handling): Mohammed
- Student 2 (Services, GUI, Testing):

---

# Project Description
A restaurant management application built with Python and OOP.
The system manages the menu, tables, customers, orders, and payments,
with data persistence through JSON files.
The desktop interface uses Python's standard-library Tkinter.

---

# Main Features
- Manage menu (Food and Drinks)
- Manage tables (available / occupied)
- Manage customers (regular / VIP)
- Create and manage orders
- Add / remove items from orders
- Calculate order totals and discounts automatically
- Process payments
- Search menu items
- Filter orders by status
- Dashboard with real data
- Save and load menu data using JSON
- Manage menu items, customers, tables, orders, and payments in the desktop interface

---

# Classes

| Class | Description |
|-------|-------------|
| `MenuItem` (Abstract) | Base class for all menu items |
| `FoodItem` | Inherits from MenuItem — food with prep_time |
| `DrinkItem` | Inherits from MenuItem — drink with size |
| `Customer` | Customer with VIP discount |
| `Table` | Restaurant table with occupied state |
| `OrderItem` | Single line in an order (Composition) |
| `Order` | Full order with items, customer, table |
| `Payment` | Payment linked to an order |
| `Restaurant` | Main manager (Composition of all) |
| `FileManager` | Handles JSON save/load |

---

# OOP Concepts Used

| Concept | Where |
|---------|-------|
| **Encapsulation** | Private attributes (`_price`, `_status`) + `@property` |
| **Inheritance** | `FoodItem` and `DrinkItem` inherit from `MenuItem` |
| **Polymorphism** | `get_details()` differs per subclass |
| **Abstraction** | `MenuItem` uses `ABC` and `@abstractmethod` |
| **Composition** | `Order` contains `OrderItem`; `Restaurant` contains all entities |
| **Type Hints** | Applied across all methods |
| **Exception Handling** | Custom `RestaurantError` hierarchy |

---

# Business Rules
1. An occupied table cannot be assigned again.
2. Quantity must be greater than zero.
3. An empty order cannot be checked out.
4. Order total is calculated automatically.
5. VIP customers receive a 10% discount.
6. Payment amount must be at least the order total.
7. Duplicate IDs are not allowed.

---

# File Storage
- **Format:** JSON
- **Location:** `data/`
- **Managed by:** `FileManager` class
- **Files:** `menu.json`, `customers.json`, `tables.json`, `orders.json`, and `payments.json`
- Menu items, customers, tables, orders, and payments load when the app starts and save when changed.
- Open orders and table reservations are restored on the next launch.
- Food preparation times, drink sizes, VIP status, order items, and payment details are preserved.

---

# How to Run
From the project directory, run:
```powershell
python main.py
```

The application opens a desktop window. Use the tabs to add menu items,
customers, and tables; create orders; add or remove order items; and take
payments. Changes are saved automatically in the matching JSON files under
`data/`.
Data-entry actions use a single form window with all required fields visible
together.

# Tests
The standard-library test suite covers the business rules shown above and
additional restaurant and JSON persistence cases. Run it from the project
directory with:
```powershell
python -B -m unittest discover -s tests -v
```