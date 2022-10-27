from ..model import user


def from_req_2_model_user(dt):
    return user.User(dt.get('username', ''), dt.get('password', ''), dt.get('fullname', ''))
