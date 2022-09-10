from ..model import user


def from_req_2_model(req):
    return user.User(req['username'], req['password'])
