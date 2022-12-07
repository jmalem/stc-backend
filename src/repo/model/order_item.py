from .item import Item
from utils import InvalidArgumentError


class OrderItem:
    """
        Order -> OrderItem -> Item
    """

    def __init__(self, item, cartonQty, unitQty, discountRp, discountPercent, notes):
        self.item = item
        self.cartonQty = cartonQty
        self.unitQty = unitQty
        self.discountRp = discountRp
        self.discountPercent = discountPercent
        self.notes = notes

    def validate(self):
        self.item.validate()
        if self.cartonQty and self.cartonQty <= 0:
            raise InvalidArgumentError('invalid cartonQty - must be greater than zero')
        if self.unitQty and self.unitQty <= 0:
            raise InvalidArgumentError('invalid unitQty - must be greater than zero')
        if self.discountRp and self.discountRp < 0:
            raise InvalidArgumentError('invalid discountRp - must be at least zero')
        if self.discountPercent and self.discountPercent < 0:
            raise InvalidArgumentError('invalid discountPercent - must be at least zero')

    def getItem(self) -> Item:
        return self.item

    def getCartonQty(self) -> str:
        return self.cartonQty

    def getUnitQty(self) -> str:
        return self.unitQty

    def getDiscountRp(self) -> str:
        return self.discountRp

    def getDiscountPercent(self) -> str:
        return self.discountPercent

    def getNotes(self) -> str:
        return self.notes
