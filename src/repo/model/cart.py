from src.repo.model.order import OrderItemSchema
from utils import InvalidArgumentError
from marshmallow import Schema, fields


class Cart:
    """
        Cart -> OrderItem -> Item
        A Cart is an incomplete order (id, customer, and createdAt)
        and it can be empty
    """

    def __init__(self, username, orderItems, notes):
        self.username = username
        self.metadata = 'cart'
        self.orderItems = orderItems
        self.notes = notes

    def validate(self):
        if self.username == '':
            raise InvalidArgumentError('invalid username')

        for order_item in self.orderItems:
            order_item.validate()

    def getUsername(self) -> str:
        return self.username

    def getOrderItems(self):
        return self.orderItems

    def getNotes(self) -> str:
        return self.notes


class CartSchema(Schema):
    username = fields.Str()
    metadata = fields.Str()
    orderItems = fields.List(fields.Nested(OrderItemSchema()))
    notes = fields.Str()
