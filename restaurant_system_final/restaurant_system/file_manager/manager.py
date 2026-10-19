import json
from pathlib import Path
from typing import Any

from models.customer import Customer
from models.menu_item import DrinkItem, FoodItem, MenuItem
from models.order import Order
from models.payment import Payment
from models.table import Table


class FileManager:
    DATA_FILES = (
        "menu.json",
        "customers.json",
        "tables.json",
        "orders.json",
        "payments.json",
    )

    def __init__(self, data_dir: str | Path | None = None) -> None:
        self._data_dir = (
            Path(data_dir)
            if data_dir is not None
            else Path(__file__).resolve().parent.parent / "data"
        )

    def ensure_data_files(self) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        for filename in self.DATA_FILES:
            path = self._data_dir / filename
            if not path.exists():
                self._write_json(filename, [])

    def _write_json(self, filename: str, data: list[dict[str, Any]]) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        path = self._data_dir / filename
        temporary_path = path.with_suffix(f"{path.suffix}.tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        temporary_path.replace(path)

    def _read_json(self, filename: str) -> list[dict[str, Any]]:
        path = self._data_dir / filename
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError(f"{path} must contain a JSON list.")
        if not all(isinstance(row, dict) for row in data):
            raise ValueError(f"Every record in {path} must be a JSON object.")
        return data

    def save_menu(self, menu: list[MenuItem]) -> None:
        data: list[dict[str, Any]] = []
        for item in menu:
            row: dict[str, Any] = {
                "type": type(item).__name__,
                "id": item.id,
                "name": item.name,
                "price": item.price,
            }
            if isinstance(item, FoodItem):
                row["prep_time"] = item.prep_time
            elif isinstance(item, DrinkItem):
                row["size"] = item.size
            data.append(row)
        self._write_json("menu.json", data)

    def load_menu(self) -> list[MenuItem]:
        items: list[MenuItem] = []
        for row in self._read_json("menu.json"):
            if row["type"] == "FoodItem":
                items.append(
                    FoodItem(
                        row["id"],
                        row["name"],
                        row["price"],
                        row.get("prep_time", 10),
                    )
                )
            elif row["type"] == "DrinkItem":
                items.append(
                    DrinkItem(
                        row["id"],
                        row["name"],
                        row["price"],
                        row.get("size", "Medium"),
                    )
                )
            else:
                raise ValueError(f"Unsupported menu item type: {row['type']}")
        return items

    def save_customers(self, customers: list[Customer]) -> None:
        self._write_json(
            "customers.json",
            [
                {
                    "id": customer.id,
                    "name": customer.name,
                    "phone": customer.phone,
                    "is_vip": customer.is_vip,
                }
                for customer in customers
            ],
        )

    def load_customers(self) -> list[Customer]:
        return [
            Customer(row["id"], row["name"], row["phone"], row["is_vip"])
            for row in self._read_json("customers.json")
        ]

    def save_tables(self, tables: list[Table]) -> None:
        self._write_json(
            "tables.json",
            [
                {"number": table.number, "capacity": table.capacity}
                for table in tables
            ],
        )

    def load_tables(self) -> list[Table]:
        return [
            Table(row["number"], row["capacity"])
            for row in self._read_json("tables.json")
        ]

    def save_orders(self, orders: list[Order]) -> None:
        self._write_json(
            "orders.json",
            [
                {
                    "id": self.order_id(index),
                    "customer_id": order.customer.id,
                    "table_number": order.table.number,
                    "status": order.status,
                    "items": [
                        {
                            "menu_item_id": item.menu_item.id,
                            "quantity": item.quantity,
                        }
                        for item in order.items
                    ],
                }
                for index, order in enumerate(orders)
            ],
        )

    def load_orders(self) -> list[dict[str, Any]]:
        return self._read_json("orders.json")

    def save_payments(self, payments: list[Payment], orders: list[Order]) -> None:
        self._write_json(
            "payments.json",
            [
                {
                    "order_id": self.order_id(
                        next(
                            index
                            for index, order in enumerate(orders)
                            if order is payment.order
                        )
                    ),
                    "amount": payment.amount,
                    "method": payment.method,
                }
                for payment in payments
            ],
        )

    def load_payments(self) -> list[dict[str, Any]]:
        return self._read_json("payments.json")

    @staticmethod
    def order_id(index: int) -> str:
        return f"O{index + 1:06d}"
