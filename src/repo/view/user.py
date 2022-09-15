from ..model import user


def from_req_2_model(dt):
    return user.User(dt['username'], dt['password'])
