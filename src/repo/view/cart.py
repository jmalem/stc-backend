from ..model import cart, order_item, item


def from_req_2_model_cart(dt):
    if dt is None:
        return None
    return cart.Cart(
        dt.get('username', ""),
        from_req_2_model_order_item_array(dt.get('orderItems', [])),
        dt.get('notes', ""),
    )


def from_req_2_model_order_item_array(arr):
    if len(arr) == 0:
        return []
    new_arr = list(map(from_req_2_model_order_item, arr))
    return new_arr


def from_req_2_model_order_item(dt):
    if dt is None:
        return None
    return order_item.OrderItem(
        from_req_2_model_item(dt.get('item')),
        dt.get('cartonQty'),
        dt.get('unitQty'),
        dt.get('discountRp', 0),
        dt.get('discountPercent', 0),
        dt.get('notes', ""),
    )


def from_req_2_model_item(dt):
    if dt is None:
        return None
    return item.Item(
        dt.get('itemId', ""),
        dt.get('title', ""),
        dt.get('category', ""),
        dt.get('displayId', ""),
        dt.get('packing', ""),
        dt.get('unit', ""),
        dt.get('unitPrice', 0),
        dt.get('imageUrl', ""),
    )
