from exceptions import InvalidQuantityError
from models.menu_item import MenuItem
from exceptions import EmptyOrderError
from exceptions import NotFoundError

class OrderItem:
    def __init__(self, menu_item: MenuItem, quantity: int) -> None:
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be greater than zero")
        self._menu_item = menu_item
        self._quantity = quantity

    @property
    def menu_item(self) -> MenuItem:
        return self._menu_item

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def subtotal(self) -> float:
        return self._menu_item.price * self._quantity
    
    
    
    
class Order:
    def __init__(self, customer, table) -> None:
        self._customer = customer
        self._table = table
        self._items: list[OrderItem] = []
        self._status = "Open"
        table.assign()

    @property
    def customer(self):
        return self._customer

    @property
    def table(self):
        return self._table

    @property
    def items(self) -> list[OrderItem]:
        return list(self._items)

    @property
    def status(self) -> str:
        return self._status

    def add_item(self, menu_item: MenuItem, quantity: int = 1) -> None:
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be greater than zero")
        for item in self._items:
            if item.menu_item.id == menu_item.id:
                item._quantity += quantity
                return
        self._items.append(OrderItem(menu_item, quantity)) 
        
    @property
    def subtotal(self) -> float:
       return sum(item.subtotal for item in self._items)

    @property
    def discount(self) -> float:
       return self.subtotal * self._customer.get_discount_rate()

    @property
    def total(self) -> float:
       return self.subtotal - self.discount  
   
    def remove_item(self, item_id: str) -> None:
       for i, item in enumerate(self._items):
           if item.menu_item.id == item_id:
              self._items.pop(i)
              return
       raise NotFoundError(f"Item {item_id} not in order")
      
      
      
    def checkout(self) -> float:
       if not self._items:
            raise EmptyOrderError("Cannot checkout an empty order")
       if self._status != "Open":
             raise EmptyOrderError("Order is already closed")
       self._status = "Paid"
       self._table.release()
       return self.total  
   
   