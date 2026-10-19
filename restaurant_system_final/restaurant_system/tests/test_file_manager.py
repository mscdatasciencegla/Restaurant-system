import json
import tempfile
import unittest
from pathlib import Path

from file_manager.manager import FileManager
from models.customer import Customer
from models.menu_item import DrinkItem, FoodItem
from models.restaurant import Restaurant
from models.table import Table


class FileManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_dir = Path(self.temp_dir.name)
        self.file_manager = FileManager(self.data_dir)

    def test_ensure_data_files_creates_separate_empty_json_files(self) -> None:
        self.file_manager.ensure_data_files()

        self.assertEqual(
            {path.name for path in self.data_dir.glob("*.json")},
            set(FileManager.DATA_FILES),
        )
        for filename in FileManager.DATA_FILES:
            with self.subTest(filename=filename):
                self.assertEqual(
                    json.loads((self.data_dir / filename).read_text(encoding="utf-8")),
                    [],
                )

    def test_ensure_data_files_does_not_overwrite_existing_data(self) -> None:
        self.file_manager.ensure_data_files()
        menu_path = self.data_dir / "menu.json"
        original = '[{"type":"FoodItem","id":"F1","name":"Soup","price":5,"prep_time":8}]'
        menu_path.write_text(original, encoding="utf-8")

        self.file_manager.ensure_data_files()

        self.assertEqual(menu_path.read_text(encoding="utf-8"), original)

    def test_menu_round_trip_preserves_food_and_drink_fields(self) -> None:
        menu = [
            FoodItem("F1", "Soup", 5.5, 12),
            DrinkItem("D1", "Tea", 2.25, "Large"),
        ]

        self.file_manager.save_menu(menu)
        loaded = self.file_manager.load_menu()

        self.assertIsInstance(loaded[0], FoodItem)
        self.assertEqual(loaded[0].prep_time, 12)
        self.assertIsInstance(loaded[1], DrinkItem)
        self.assertEqual(loaded[1].size, "Large")
        self.assertEqual([item.price for item in loaded], [5.5, 2.25])

    def test_customers_tables_orders_and_payments_are_serialized(self) -> None:
        restaurant = Restaurant("Test Restaurant")
        restaurant.add_menu_item(FoodItem("F1", "Soup", 10.0, 12))
        restaurant.add_customer(Customer("C1", "Alex", "555-0100", is_vip=True))
        restaurant.add_customer(Customer("C2", "Sam", "555-0101"))
        restaurant.add_table(Table(1, 4))
        restaurant.add_table(Table(2, 2))

        paid_order = restaurant.create_order("C1", 1)
        paid_order.add_item(restaurant.find_menu_item("F1"), 2)
        restaurant.pay_order(paid_order, 25.0, "Card")
        open_order = restaurant.create_order("C2", 2)
        open_order.add_item(restaurant.find_menu_item("F1"), 1)

        self.file_manager.save_customers(restaurant.customers)
        self.file_manager.save_tables(restaurant.tables)
        self.file_manager.save_orders(restaurant.orders)
        self.file_manager.save_payments(restaurant.payments, restaurant.orders)

        loaded_customers = self.file_manager.load_customers()
        loaded_tables = self.file_manager.load_tables()
        loaded_orders = self.file_manager.load_orders()
        loaded_payments = self.file_manager.load_payments()

        self.assertEqual([customer.id for customer in loaded_customers], ["C1", "C2"])
        self.assertTrue(loaded_customers[0].is_vip)
        self.assertEqual(
            [(table.number, table.capacity) for table in loaded_tables],
            [(1, 4), (2, 2)],
        )
        self.assertEqual(
            [(order["id"], order["status"]) for order in loaded_orders],
            [("O000001", "Paid"), ("O000002", "Open")],
        )
        self.assertEqual(
            loaded_orders[0]["items"],
            [{"menu_item_id": "F1", "quantity": 2}],
        )
        self.assertEqual(
            loaded_orders[1]["items"],
            [{"menu_item_id": "F1", "quantity": 1}],
        )
        self.assertEqual(
            loaded_payments,
            [{"order_id": "O000001", "amount": 25.0, "method": "Card"}],
        )

    def test_invalid_json_root_shape_is_reported(self) -> None:
        (self.data_dir / "customers.json").write_text(
            '{"id":"C1"}', encoding="utf-8"
        )

        with self.assertRaisesRegex(ValueError, "must contain a JSON list"):
            self.file_manager.load_customers()


if __name__ == "__main__":
    unittest.main()
