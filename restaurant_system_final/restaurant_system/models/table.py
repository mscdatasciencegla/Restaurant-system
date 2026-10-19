from exceptions import TableOccupiedError


class Table:
    def __init__(self, number: int, capacity: int) -> None:
        self._number = number
        self._capacity = capacity
        self._is_occupied = False

    @property
    def number(self) -> int:
        return self._number

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def is_occupied(self) -> bool:
        return self._is_occupied

    def assign(self) -> None:
        if self._is_occupied:
            raise TableOccupiedError(f"Table {self._number} is already occupied")
        self._is_occupied = True

    def release(self) -> None:
        self._is_occupied = False
