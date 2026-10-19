from abc import ABC, abstractmethod


class MenuItem(ABC):
    def __init__(self, item_id: str, name: str, price: float) -> None:
        self._id = item_id
        self._name = name
        self._price = price
        self._is_available = True
        if price <= 0:
            raise ValueError("Price must be greater than zero")
        
    @property
    def is_available(self) -> bool:
        return self._is_available
               
    
    @property
    def price(self) -> float:
        return self._price
      
 
    @property
    def id(self) -> str:
        return self._id
     

    @property
    def name(self) -> str:
        return self._name
     
 
    
    @abstractmethod
    def get_details(self) -> str:
        pass    
    
    
    
    
    

    
    
class DrinkItem(MenuItem):
    def __init__(self, item_id: str, name: str, price: float, size: str) -> None:
        super().__init__(item_id, name, price)
        self._size = size

    @property
    def size(self) -> str:
        return self._size

    def get_details(self) -> str:
        return f"[Drink] {self._name} - {self._price} ({self._size})"
    


class FoodItem(MenuItem):
    def __init__(self, item_id: str, name: str, price: float, prep_time: int) -> None:
        super().__init__(item_id, name, price)
        self._prep_time = prep_time

    @property
    def prep_time(self) -> int:
        return self._prep_time

    def get_details(self) -> str:
        return f"[Food] {self._name} - {self._price} (prep: {self._prep_time}m)"
    
    