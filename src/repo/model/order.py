import uuid
from utils import InvalidArgumentError
from marshmallow import Schema, fields


class Order:
    """
        Order -> OrderItem -> Item
    """

    def __init__(self, customer, created_by, order_items, notes, created_at, modified_at):
        self.id = uuid.uuid4().__str__()
        self.customer = customer
        self.created_by = created_by
        self.order_items = order_items
        self.notes = notes
        self.created_at = created_at

    def validate(self):
        if self.id == '':
            raise InvalidArgumentError('invalid id')

        if self.customer == '':
            raise InvalidArgumentError('invalid customer')

        if self.created_by == '':
            raise InvalidArgumentError('invalid created_by')

        if len(self.order_items) == 0:
            raise InvalidArgumentError('order_items cannot be empty')

        for order_item in self.order_items:
            order_item.validate()

    def get_id(self) -> str:
        return self.id

    def get_customer(self) -> str:
        return self.customer

    def get_created_by(self) -> str:
        return self.created_by

    def get_order_items(self):
        return self.order_items

    def get_notes(self) -> str:
        return self.notes


class ItemSchema(Schema):
    item_id = fields.Str()
    title = fields.Str()
    category = fields.Str()
    display_id = fields.Str()
    packing = fields.Str()
    unit = fields.Str()
    unit_price = fields.Decimal()
    image_url = fields.Str()


class OrderItemSchema(Schema):
    item = fields.Nested(ItemSchema())
    carton_qty = fields.Decimal()
    unit_qty = fields.Decimal()
    discount_rp = fields.Decimal()
    discount_percent = fields.Decimal()
    notes = fields.Str()


class OrderSchema(Schema):
    id = fields.Str()
    customer = fields.Str()
    created_by = fields.Str()
    order_items = fields.List(fields.Nested(OrderItemSchema()))
    notes = fields.Str()
    created_at = fields.Str()
