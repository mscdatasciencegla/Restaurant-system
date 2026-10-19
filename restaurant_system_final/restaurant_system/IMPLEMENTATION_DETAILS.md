# Changes Made During This Session

This file records only the project changes made during this chat session. It
is a change log, not a general description of the restaurant project.

## 1. Made the project launch with a working data path

- Updated [`file_manager/manager.py`](./file_manager/manager.py) so its default
  data directory is the project's own `data/` folder, resolved relative to the
  module, instead of a hardcoded `D:/restaurant_system/data` path.
- Switched file handling to `pathlib.Path` so path construction works with the
  project's Windows location without relying on a specific drive or install
  folder.
- Updated [`main.py`](./main.py) from a hardcoded console demo into the normal
  desktop-app entry point. Running `python main.py` now launches the GUI.
- Updated [`readme.md`](./readme.md) with the desktop launch instructions.
- Ran the demo after fixing the path and confirmed it completed its save
  operation successfully.

## 2. Implemented the desktop GUI

Added [`gui/app.py`](./gui/app.py), which contains the Tkinter application and
connects the interface to the existing restaurant model operations.

The interface includes:

- A dashboard with menu, customer, available-table, order, and payment totals.
- Menu listing and live search by item name or ID.
- Customer listing with regular/VIP status.
- Table listing with capacity and current availability.
- An order list, order-item details, subtotal, discount, total, and status
  filtering.
- GUI actions to add menu items, customers, and tables; create orders; add or
  remove order items; and take payments.
- Validation feedback for invalid input and business-rule failures.

## 3. Restyled the GUI

Restyled [`gui/app.py`](./gui/app.py) into a restaurant point-of-sale layout:

- Added forest-green sidebar navigation for Dashboard, Menu, Customers,
  Tables, and Orders.
- Added a warm cream content background, white cards, orange primary actions,
  and updated table styling.
- Added active-page highlighting, a status indicator, dashboard metric cards,
  and alternating row colors.
- Preserved and smoke-tested the existing workflows after restyling.

## 4. Changed data entry to single-window forms

Replaced the sequence of pop-up questions with forms that show each action's
required fields together:

- Menu item form: type, ID, name, price, and the matching food preparation-time
  or drink-size field.
- Customer form: ID, name, phone, and regular/VIP membership.
- Table form: number and seating capacity.
- Order form: customer and available table dropdowns.
- Add-order-item form: menu item and quantity.
- Payment form: amount received and payment method.

Forms validate required fields and show errors inline. The menu form reports
duplicate item IDs before submission, and the other forms keep the dialog open
when the operation is rejected.

## 5. Added persistence for each data category

Extended [`file_manager/manager.py`](./file_manager/manager.py) and connected
it to [`gui/app.py`](./gui/app.py) so the application stores records in
separate JSON files:

- `data/menu.json`
- `data/customers.json`
- `data/tables.json`
- `data/orders.json`
- `data/payments.json`

The persistence changes:

- Create missing JSON files as empty lists without overwriting existing files.
- Save data after successful GUI changes and load it on application startup.
- Preserve food preparation times, drink sizes, and VIP customer status.
- Store order references by customer ID, table number, and menu-item ID.
- Store payment references by generated order ID.
- Restore open orders and reserve their tables after restart.
- Restore paid orders from their matching payment records, leaving their tables
  available.
- Report malformed JSON, missing records, and inconsistent order/payment
  references rather than silently ignoring them.
- Write JSON to a temporary file before replacing the destination file.

Added a `payments` read-only property to
[`models/restaurant.py`](./models/restaurant.py) so persistence can serialize
the restaurant's recorded payments.

## 6. Added business-rule and persistence tests

Added two standard-library `unittest` modules:

- [`tests/test_business_rules.py`](./tests/test_business_rules.py) covers
  occupied-table rejection and release, positive quantities, empty orders,
  totals, VIP and regular-customer discounts, duplicate/missing records,
  insufficient and repeated payments, exact payment, change, and table release.
- [`tests/test_file_manager.py`](./tests/test_file_manager.py) covers creation
  of all five JSON files, preservation of existing files, menu metadata
  round-tripping, customer/table/order/payment serialization, and malformed
  JSON shape reporting.

The business tests exposed a quantity-validation gap: `Order.add_item` checked
quantity for a new line through `OrderItem`, but could add zero or a negative
quantity to a line that already existed. Updated
[`models/order.py`](./models/order.py) to validate quantity before either path.

Added the test command to [`readme.md`](./readme.md):

```powershell
python -B -m unittest discover -s tests -v
```

The suite was run after the changes: **23 tests passed**.

## 7. Updated project documentation

- Rewrote [`handover.md`](./handover.md) to match the implemented GUI,
  persistence files, test suite, run instructions, and current limitations.
- Updated [`readme.md`](./readme.md) with GUI launch instructions, persistent
  data-file information, and the test command.
- Created this file as a detailed record of session changes only.

## Validation performed during this session

- Ran `python main.py` and confirmed the demo's data-save operation succeeded
  after correcting its hardcoded path; the entry point was later changed to
  launch the GUI.
- Smoke-tested GUI window construction and navigation.
- Exercised menu form submissions for both food and drinks, including saved
  item-specific fields and duplicate-ID feedback.
- Exercised customer, table, order, item-add/remove, and payment GUI callbacks,
  including duplicate records, VIP totals, insufficient payment, successful
  payment, and table release.
- Tested JSON persistence using temporary directories, including application
  restart restoration of open and paid orders.
- Ran the complete 23-test `unittest` suite successfully.
