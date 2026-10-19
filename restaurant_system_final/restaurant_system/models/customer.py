class Customer:
    def __init__(self, customer_id: str, name: str, phone: str, is_vip: bool = False) -> None:
        self._id = customer_id
        self._name = name
        self._phone = phone
        self._is_vip = is_vip

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def phone(self) -> str:
        return self._phone

    @property
    def is_vip(self) -> bool:
        return self._is_vip

    def get_discount_rate(self) -> float:
        return 0.10 if self._is_vip else 0.0