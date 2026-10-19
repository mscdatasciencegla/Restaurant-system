from datetime import datetime
from exceptions import PaymentError
from models.order import Order


class Payment:
    def __init__(self, order: Order, amount: float, method: str = "Cash") -> None:
        if order.status != "Open":
            raise PaymentError("Order is not open for payment")
        if amount < order.total:
            raise PaymentError(f"Insufficient amount. Required: {order.total:.2f}")
        self._order = order
        self._amount = amount
        self._method = method
        self._paid_at = datetime.now()
        self._change = amount - order.total
        order.checkout()

    @property
    def order(self) -> Order:
        return self._order

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def method(self) -> str:
        return self._method

    @property
    def change(self) -> float:
        return self._change