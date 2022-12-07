import uuid
from utils import InvalidArgumentError
from marshmallow import Schema, fields


class Order:
    """
        Order -> OrderItem -> Item
    """

    def __init__(self, customer, createdBy, orderItems, notes, createdAt, modifiedAt):
        self.id = uuid.uuid4().__str__()
        self.customer = customer
        self.createdBy = createdBy
        self.orderItems = orderItems
        self.notes = notes
        self.createdAt = createdAt

    def validate(self):
        if self.id == '':
            raise InvalidArgumentError('invalid id')

        if self.customer == '':
            raise InvalidArgumentError('invalid customer')

        if self.createdBy == '':
            raise InvalidArgumentError('invalid createdBy')

        if len(self.orderItems) == 0:
            raise InvalidArgumentError('orderItems cannot be empty')

        for order_item in self.orderItems:
            order_item.validate()

    def getId(self) -> str:
        return self.id

    def getCustomer(self) -> str:
        return self.customer

    def getCreatedBy(self) -> str:
        return self.createdBy

    def getOrderItems(self):
        return self.orderItems

    def getNotes(self) -> str:
        return self.notes


class ItemSchema(Schema):
    itemId = fields.Str()
    title = fields.Str()
    category = fields.Str()
    displayId = fields.Str()
    packing = fields.Str()
    unit = fields.Str()
    unitPrice = fields.Decimal()
    imageUrl = fields.Str()


class OrderItemSchema(Schema):
    item = fields.Nested(ItemSchema())
    cartonQty = fields.Decimal()
    unitQty = fields.Decimal()
    discountRp = fields.Decimal()
    discountPercent = fields.Decimal()
    notes = fields.Str()


class OrderSchema(Schema):
    id = fields.Str()
    customer = fields.Str()
    createdBy = fields.Str()
    orderItems = fields.List(fields.Nested(OrderItemSchema()))
    notes = fields.Str()
    createdAt = fields.Str()
