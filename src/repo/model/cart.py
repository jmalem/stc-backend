from src.repo.model.order import OrderItemSchema
from utils import InvalidArgumentError
from marshmallow import Schema, fields


class Cart:
    """
        Cart -> OrderItem -> Item
        A Cart is an incomplete order (id, customer, and createdAt)
        and it can be empty
    """

    def __init__(self, username, orderItems, notes, discountRp, discountPercent, customer):
        self.username = username
        self.metadata = 'cart'
        self.orderItems = orderItems
        self.notes = notes
        self.discountRp = discountRp
        self.discountPercent = discountPercent
        self.customer = customer

    def validate(self):
        if self.username == '':
            raise InvalidArgumentError('invalid username')
        if self.discountRp and self.discountRp < 0:
            raise InvalidArgumentError('invalid discountRp - must be at least zero')
        if self.discountPercent and self.discountPercent < 0:
            raise InvalidArgumentError('invalid discountPercent - must be at least zero')

        for order_item in self.orderItems:
            order_item.validate()

    def getUsername(self) -> str:
        return self.username

    def getOrderItems(self):
        return self.orderItems

    def getNotes(self) -> str:
        return self.notes

    def getDiscountRp(self) -> int:
        return self.discountRp

    def getDiscountPercent(self) -> int:
        return self.discountPercent

    def getCustomer(self) -> str:
        return self.customer


class CartSchema(Schema):
    username = fields.Str()
    metadata = fields.Str()
    orderItems = fields.List(fields.Nested(OrderItemSchema()))
    notes = fields.Str()
    discountRp = fields.Decimal()
    discountPercent = fields.Decimal()
    customer = fields.Str()
