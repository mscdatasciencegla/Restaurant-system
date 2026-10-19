import unittest

from exceptions import (
    EmptyOrderError,
    InvalidQuantityError,
    NotFoundError,
    PaymentError,
    RestaurantError,
    TableOccupiedError,
)
from models.customer import Customer
from models.menu_item import DrinkItem, FoodItem
from models.restaurant import Restaurant
from models.table import Table


class TableTests(unittest.TestCase):
    def test_occupied_table_cannot_be_assigned_again(self) -> None:
        table = Table(1, 4)

        table.assign()

        self.assertTrue(table.is_occupied)
        with self.assertRaises(TableOccupiedError):
            table.assign()

    def test_releasing_table_makes_it_available_again(self) -> None:
        table = Table(1, 4)
        table.assign()

        table.release()

        self.assertFalse(table.is_occupied)
        table.assign()
        self.assertTrue(table.is_occupied)


class OrderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.restaurant = Restaurant("Test Restaurant")
        self.customer = Customer("C1", "Alex", "555-0100", is_vip=True)
        self.table = Table(1, 4)
        self.restaurant.add_customer(self.customer)
        self.restaurant.add_table(self.table)
        self.order = self.restaurant.create_order("C1", 1)
        self.food = FoodItem("F1", "Soup", 10.0, 12)
        self.drink = DrinkItem("D1", "Tea", 2.5, "Large")

    def test_order_item_quantity_must_be_positive(self) -> None:
        for quantity in (0, -1):
            with self.subTest(quantity=quantity):
                with self.assertRaises(InvalidQuantityError):
                    self.order.add_item(self.food, quantity)

        self.assertEqual(self.order.items, [])

    def test_nonpositive_quantity_is_rejected_when_item_already_exists(self) -> None:
        self.order.add_item(self.food, 2)

        for quantity in (0, -1):
            with self.subTest(quantity=quantity):
                with self.assertRaises(InvalidQuantityError):
                    self.order.add_item(self.food, quantity)

        self.assertEqual(self.order.items[0].quantity, 2)

    def test_empty_order_cannot_be_checked_out(self) -> None:
        with self.assertRaises(EmptyOrderError):
            self.order.checkout()

        self.assertEqual(self.order.status, "Open")
        self.assertTrue(self.table.is_occupied)

    def test_order_totals_and_vip_discount_are_calculated(self) -> None:
        self.order.add_item(self.food, 2)
        self.order.add_item(self.drink, 1)

        self.assertEqual(self.order.subtotal, 22.5)
        self.assertEqual(self.order.discount, 2.25)
        self.assertEqual(self.order.total, 20.25)

    def test_adding_same_item_updates_quantity_and_total(self) -> None:
        self.order.add_item(self.food, 1)
        self.order.add_item(self.food, 2)

        self.assertEqual(len(self.order.items), 1)
        self.assertEqual(self.order.items[0].quantity, 3)
        self.assertEqual(self.order.total, 27.0)

    def test_removing_item_recalculates_order_total(self) -> None:
        self.order.add_item(self.food, 2)
        self.order.add_item(self.drink, 1)

        self.order.remove_item("F1")

        self.assertEqual(self.order.subtotal, 2.5)
        self.assertEqual(self.order.discount, 0.25)
        self.assertEqual(self.order.total, 2.25)

    def test_regular_customer_receives_no_vip_discount(self) -> None:
        restaurant = Restaurant("Test Restaurant")
        restaurant.add_customer(Customer("C2", "Sam", "555-0101"))
        restaurant.add_table(Table(2, 2))
        order = restaurant.create_order("C2", 2)
        order.add_item(self.food, 2)

        self.assertEqual(order.subtotal, 20.0)
        self.assertEqual(order.discount, 0.0)
        self.assertEqual(order.total, 20.0)

    def test_removing_missing_item_raises_not_found(self) -> None:
        with self.assertRaises(NotFoundError):
            self.order.remove_item("missing")


class RestaurantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.restaurant = Restaurant("Test Restaurant")

    def test_duplicate_menu_customer_and_table_ids_are_rejected(self) -> None:
        self.restaurant.add_menu_item(FoodItem("F1", "Soup", 5.0, 8))
        self.restaurant.add_customer(Customer("C1", "Alex", "555-0100"))
        self.restaurant.add_table(Table(1, 4))

        with self.assertRaises(RestaurantError):
            self.restaurant.add_menu_item(FoodItem("F1", "Salad", 4.0, 5))
        with self.assertRaises(RestaurantError):
            self.restaurant.add_customer(Customer("C1", "Sam", "555-0101"))
        with self.assertRaises(RestaurantError):
            self.restaurant.add_table(Table(1, 2))

    def test_creating_order_on_occupied_table_is_rejected(self) -> None:
        self.restaurant.add_customer(Customer("C1", "Alex", "555-0100"))
        table = Table(1, 4)
        self.restaurant.add_table(table)
        self.restaurant.create_order("C1", 1)

        with self.assertRaises(TableOccupiedError):
            self.restaurant.create_order("C1", 1)

        self.assertEqual(len(self.restaurant.orders), 1)

    def test_unknown_menu_customer_and_table_are_not_found(self) -> None:
        with self.assertRaises(NotFoundError):
            self.restaurant.find_menu_item("missing")
        with self.assertRaises(NotFoundError):
            self.restaurant.find_customer("missing")
        with self.assertRaises(NotFoundError):
            self.restaurant.get_table(999)


class PaymentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.restaurant = Restaurant("Test Restaurant")
        self.restaurant.add_customer(Customer("C1", "Alex", "555-0100"))
        self.restaurant.add_table(Table(1, 4))
        self.restaurant.add_menu_item(FoodItem("F1", "Soup", 10.0, 12))
        self.order = self.restaurant.create_order("C1", 1)
        self.order.add_item(self.restaurant.find_menu_item("F1"), 2)

    def test_insufficient_payment_does_not_close_order_or_release_table(self) -> None:
        with self.assertRaises(PaymentError):
            self.restaurant.pay_order(self.order, 19.99, "Cash")

        self.assertEqual(self.order.status, "Open")
        self.assertTrue(self.order.table.is_occupied)
        self.assertEqual(self.restaurant.payments, [])

    def test_successful_payment_closes_order_and_releases_table(self) -> None:
        payment = self.restaurant.pay_order(self.order, 25.0, "Card")

        self.assertEqual(payment.change, 5.0)
        self.assertEqual(payment.method, "Card")
        self.assertEqual(self.order.status, "Paid")
        self.assertFalse(self.order.table.is_occupied)
        self.assertEqual(self.restaurant.payments, [payment])

    def test_paid_order_cannot_be_paid_twice(self) -> None:
        self.restaurant.pay_order(self.order, 20.0)

        with self.assertRaises(PaymentError):
            self.restaurant.pay_order(self.order, 20.0)

    def test_exact_payment_has_no_change(self) -> None:
        payment = self.restaurant.pay_order(self.order, 20.0)

        self.assertEqual(payment.change, 0.0)
        self.assertEqual(self.order.status, "Paid")

    def test_empty_order_cannot_be_paid(self) -> None:
        restaurant = Restaurant("Test Restaurant")
        restaurant.add_customer(Customer("C1", "Alex", "555-0100"))
        table = Table(1, 4)
        restaurant.add_table(table)
        order = restaurant.create_order("C1", 1)

        with self.assertRaises(EmptyOrderError):
            restaurant.pay_order(order, 0.0)

        self.assertEqual(order.status, "Open")
        self.assertTrue(table.is_occupied)
        self.assertEqual(restaurant.payments, [])


if __name__ == "__main__":
    unittest.main()
