from flask import abort, make_response


def get_or_abort(model, item_id):

    try:
        item_id = int(item_id)
    except:
        abort(make_response({"message": f"{model.__name__} {item_id} invalid."}, 400))

    item = model.query.get(item_id)

    if not item:
        abort(make_response({"message": f"{model.__name__} {item_id} not found."}, 404))

    return item
