class RestaurantError(Exception):
    pass


class TableOccupiedError(RestaurantError):
    pass


class InvalidQuantityError(RestaurantError):
    pass

class PaymentError(RestaurantError):
    pass


class NotFoundError(RestaurantError):
    pass


class EmptyOrderError(RestaurantError):
    pass