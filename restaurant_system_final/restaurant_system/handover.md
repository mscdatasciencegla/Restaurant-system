# Restaurant Management System — Handover

## Project status

The project is a Python desktop restaurant-management application. The normal
entry point, [`main.py`](./main.py), launches the Tkinter GUI. The application
uses the existing model classes for its restaurant rules and JSON files in
[`data/`](./data/) for persistent storage.

## Run the application and tests

Run these commands from the project directory:

```powershell
python main.py
python -B -m unittest discover -s tests -v
```

Tkinter is part of the Python standard library; no third-party GUI package is
required. The tests use the standard-library `unittest` framework.

## Project structure

```text
restaurant_system/
├── main.py
├── exceptions.py
├── models/
│   ├── menu_item.py
│   ├── customer.py
│   ├── table.py
│   ├── order.py
│   ├── payment.py
│   └── restaurant.py
├── file_manager/
│   └── manager.py
├── gui/
│   └── app.py
├── data/
│   ├── menu.json
│   ├── customers.json
│   ├── tables.json
│   ├── orders.json
│   └── payments.json
└── tests/
    ├── test_business_rules.py
    └── test_file_manager.py
```

## Application areas

- **GUI:** [`gui/app.py`](./gui/app.py) contains the dashboard, navigation,
  menu search, tables, customers, order details, and single-window data-entry
  forms. The interface is built with Tkinter and themed for a restaurant
  point-of-sale workflow.
- **Models:** [`models/`](./models/) holds the restaurant entities and business
  logic. `Restaurant` coordinates menu items, customers, tables, orders, and
  payments.
- **Persistence:** [`file_manager/manager.py`](./file_manager/manager.py)
  reads and writes the JSON data files. It creates any missing data files
  without replacing files that already exist.
- **Tests:** [`tests/`](./tests/) covers the business rules and JSON
  serialization behavior.

## JSON data and persistence

The default data directory is the project's `data/` directory. The files are:

| File | Contents |
| --- | --- |
| `menu.json` | Food and drink items, including food preparation time and drink size |
| `customers.json` | Customer ID, name, phone, and VIP flag |
| `tables.json` | Table number and seating capacity |
| `orders.json` | Order ID, customer/table references, status, and menu item quantities |
| `payments.json` | Paid order reference, payment amount, and payment method |

The GUI loads records at startup and persists changes after successful
operations. Open orders reserve their tables again after restart. Paid orders
are restored together with their payment records, and their tables are
available again.

The JSON files are human-readable and can be backed up by copying the `data/`
directory while the application is closed. If a file is malformed or contains
inconsistent order/payment references, startup reports an error rather than
silently ignoring the data.

## Business rules

- Menu item IDs, customer IDs, and table numbers must be unique within their
  respective collections.
- A table cannot be assigned while occupied.
- An order-item quantity must be greater than zero, including when increasing
  the quantity of an existing line.
- VIP customers receive a 10% discount; regular customers do not.
- An empty order cannot be checked out or paid.
- Payments must be at least the order total.
- Successful payment marks an order as `Paid` and releases its table.
- Item removal updates the order total automatically.

Custom business exceptions are defined in [`exceptions.py`](./exceptions.py).

## Test coverage

[`test_business_rules.py`](./tests/test_business_rules.py) verifies table
occupancy, quantity checks, empty orders, order calculations, VIP discounts,
duplicate and missing records, and payment behavior.

[`test_file_manager.py`](./tests/test_file_manager.py) verifies the separate
JSON files, safe initialization, menu metadata round trips, serialization of
customers/tables/orders/payments, and invalid JSON structure reporting.

The current suite contains 23 tests. Run the command above after changing
models, persistence, or order/payment workflows.

## Current scope and limitations

- The application is a local desktop app using JSON files, not a networked or
  multi-user system.
- Menu, customer, table, order, and payment data persist. There is no separate
  employee/login system or database.
- Orders currently support `Open` and `Paid` statuses in the running
  application and persistence loader.
- GUI actions add records and manage orders; there are no general edit/delete
  screens for existing menu items, customers, or tables.
- The table model tracks occupancy and capacity, but order creation does not
  currently validate party size against table capacity.

## Design notes for future changes

- Keep GUI code focused on collecting input and presenting results; place
  business rules in the model classes.
- When adding a persisted field, update both its save and load paths and add a
  serialization test.
- When adding a new order status, update restoration logic and add tests for
  the status lifecycle.
- Keep tests isolated with temporary directories; do not write test data into
  the project's real `data/` directory.
