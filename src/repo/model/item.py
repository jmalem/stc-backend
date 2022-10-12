from utils import InvalidArgumentError


class Item:
    """
        Order -> OrderItem -> Item
    """
    def __init__(self, item_id, title, category, display_id, packing, unit, unit_price, image_url):
        self.item_id = item_id
        self.title = title
        self.category = category
        self.display_id = display_id
        self.packing = packing
        self.unit = unit
        self.unit_price = unit_price
        self.image_url = image_url

    def validate(self):
        if self.item_id == '':
            raise InvalidArgumentError('invalid item_id')

        if self.title == '':
            raise InvalidArgumentError('invalid title')

        if self.category == '':
            raise InvalidArgumentError('invalid category')

        if self.display_id == '':
            raise InvalidArgumentError('invalid display_id')

        if self.packing == '':
            raise InvalidArgumentError('invalid packing')

        if self.unit == '':
            raise InvalidArgumentError('invalid unit')

        if self.unit_price <= 0:
            raise InvalidArgumentError('invalid unit price')

    def get_item_id(self) -> str:
        return self.item_id

    def get_title(self) -> str:
        return self.title

    def get_category(self) -> str:
        return self.category

    def get_display_id(self) -> str:
        return self.display_id

    def get_packing(self) -> str:
        return self.packing

    def get_unit(self) -> str:
        return self.unit

    def get_unit_price(self) -> int:
        return self.unit_price

    def get_image_url(self) -> str:
        return self.image_url
