from .item import Item
from utils import InvalidArgumentError


class OrderItem:
    """
        Order -> OrderItem -> Item
    """

    def __init__(self, item, carton_qty, unit_qty, discount_rp, discount_percent, notes):
        self.item = item
        self.carton_qty = carton_qty
        self.unit_qty = unit_qty
        self.discount_rp = discount_rp
        self.discount_percent = discount_percent
        self.notes = notes

    def validate(self):
        self.item.validate()
        if self.carton_qty and self.carton_qty <= 0:
            raise InvalidArgumentError('invalid carton_qty - must be greater than zero')
        if self.unit_qty and self.unit_qty <= 0:
            raise InvalidArgumentError('invalid unit_qty - must be greater than zero')
        if self.discount_rp and self.discount_rp < 0:
            raise InvalidArgumentError('invalid discount_rp - must be at least zero')
        if self.discount_percent and self.discount_percent < 0:
            raise InvalidArgumentError('invalid discount_percent - must be at least zero')

    def get_item(self) -> Item:
        return self.item

    def get_carton_qty(self) -> str:
        return self.carton_qty

    def get_unit_qty(self) -> str:
        return self.unit_qty

    def get_discount_rp(self) -> str:
        return self.discount_rp

    def get_discount_percent(self) -> str:
        return self.discount_percent

    def get_notes(self) -> str:
        return self.notes
