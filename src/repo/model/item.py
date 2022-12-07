from utils import InvalidArgumentError


class Item:
    """
        Order -> OrderItem -> Item
    """
    def __init__(self, itemId, title, category, displayId, packing, unit, unitPrice, imageUrl):
        self.itemId = itemId
        self.title = title
        self.category = category
        self.displayId = displayId
        self.packing = packing
        self.unit = unit
        self.unitPrice = unitPrice
        self.imageUrl = imageUrl

    def validate(self):
        if self.itemId == '':
            raise InvalidArgumentError('invalid itemId')

        if self.title == '':
            raise InvalidArgumentError('invalid title')

        if self.displayId == '':
            raise InvalidArgumentError('invalid displayId')

        if self.packing == '':
            raise InvalidArgumentError('invalid packing')

        if self.unit == '':
            raise InvalidArgumentError('invalid unit')

        if self.unitPrice <= 0:
            raise InvalidArgumentError('invalid unit price')

    def getItemId(self) -> str:
        return self.itemId

    def getTitle(self) -> str:
        return self.title

    def getCategory(self) -> str:
        return self.category

    def getDisplayId(self) -> str:
        return self.displayId

    def getPacking(self) -> str:
        return self.packing

    def getUnit(self) -> str:
        return self.unit

    def getUnitPrice(self) -> int:
        return self.unitPrice

    def getImageUrl(self) -> str:
        return self.imageUrl
