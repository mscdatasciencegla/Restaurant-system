from models.menu_item import MenuItem
from models.customer import Customer
from models.table import Table
from models.order import Order
from models.payment import Payment
from exceptions import NotFoundError, RestaurantError


class Restaurant:
    def __init__(self, name: str) -> None:
        self._name = name
        self._menu: dict[str, MenuItem] = {}
        self._customers: dict[str, Customer] = {}
        self._tables: dict[int, Table] = {}
        self._orders: list[Order] = []
        self._payments: list[Payment] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def menu(self) -> list[MenuItem]:
        return list(self._menu.values())

    @property
    def customers(self) -> list[Customer]:
        return list(self._customers.values())

    @property
    def tables(self) -> list[Table]:
        return list(self._tables.values())

    @property
    def orders(self) -> list[Order]:
        return list(self._orders)

    @property
    def payments(self) -> list[Payment]:
        return list(self._payments)
    
    
    def add_menu_item(self, item: MenuItem) -> None:
      if item.id in self._menu:
        raise RestaurantError(f"Item ID {item.id} already exists")
      self._menu[item.id] = item

    def add_customer(self, customer: Customer) -> None:
      if customer.id in self._customers:
        raise RestaurantError(f"Customer ID {customer.id} exists")
      self._customers[customer.id] = customer

    def add_table(self, table: Table) -> None:
      if table.number in self._tables:
        raise RestaurantError(f"Table {table.number} exists")
      self._tables[table.number] = table
      
      
      
    def find_menu_item(self, item_id: str) -> MenuItem:
         item = self._menu.get(item_id)
         if not item:
            raise NotFoundError(f"Menu item {item_id} not found")
         return item  
     
        
     
        
    def find_customer(self, customer_id: str) -> Customer:
        c = self._customers.get(customer_id)
        if not c:
            raise NotFoundError(f"Customer {customer_id} not found")
        return c
    
    
    def get_table(self, number: int) -> Table:
        t = self._tables.get(number)
        if not t:
            raise NotFoundError(f"Table {number} not found")
        return t
    
    
    def create_order(self, customer_id: str, table_number: int) -> Order:
        customer = self.find_customer(customer_id)
        table = self.get_table(table_number)
        order = Order(customer, table)
        self._orders.append(order)
        return order
    
    
    
    def pay_order(self, order: Order, amount: float, method: str = "Cash") -> Payment:
        payment = Payment(order, amount, method)
        self._payments.append(payment)
        return payment
    
    def search_menu(self, query: str) -> list[MenuItem]:
       q = query.lower().strip()
       return [i for i in self._menu.values() if q in i.name.lower()]

    def filter_orders(self, status: str) -> list[Order]:
      return [o for o in self._orders if o.status == status]

    def available_tables(self) -> list[Table]:
       return [t for t in self._tables.values() if not t.is_occupied]
        
     
        
    def get_dashboard(self) -> dict:
        total_sales = sum(p.amount for p in self._payments)
        return {
        "menu_count": len(self._menu),
        "customers_count": len(self._customers),
        "tables_total": len(self._tables),
        "tables_available": len(self.available_tables()),
        "orders_count": len(self._orders),
        "total_sales": total_sales,
    }