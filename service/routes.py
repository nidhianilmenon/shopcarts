"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort, make_response

# , Flask
from .utils import status  # HTTP Status Codes
from service.models import Shopcart, Product

# Import Flask application
from . import app

import logging


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# RETRIEVE A SHOP CART
######################################################################
@app.route("/shopcarts/<int:id>", methods=["GET"])
def get_shopcarts(id):
    """
    Retrieve a shopcart of a customer
    This endpoint will return a shopcart based on it's id
    """
    app.logger.info("Request for Shopcart with id: %s", id)
    shopcart = Shopcart.find_by_id(id)
    if not shopcart:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Shopcart with id '{id}' could not be found.",
        )

    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING SHOPCART
######################################################################
@app.route("/shopcarts/<int:id>", methods=["PUT"])
def update_shopcarts(id):
    """
    Update a Shopcart
    This endpoint will update a Shopcart based the body that is posted
    """
    app.logger.info("Request to Update a Shop Cart with id [%s]", id)
    check_content_type("application/json")

    shopcart = Shopcart.find_by_id(id)
    if not shopcart:
        abort(status.HTTP_404_NOT_FOUND, f"Pet with id '{id}' was not found.")

    data = request.get_json()
    app.logger.info(data)
    shopcart.deserialize(data)
    shopcart.id = id
    shopcart.update()
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A SHOPCART
######################################################################
@app.route("/shopcarts/<int:id>", methods=["DELETE"])
def delete_shopcarts(id):
    """
    Delete a Shopcart
    This endpoint will delete a Shopcart based the id specified in the path
    """
    app.logger.info("Request to delete shopcart with id: %s", id)
    shopcart = Shopcart.find_by_id(id)
    if shopcart:
        shopcart.delete()
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# CREATE A NEW SHOP CART
######################################################################
@app.route("/shopcarts/<int:id>", methods=["POST"])
def create_shopcarts(id):
    """
    Creates a Shopcart
    This endpoint will create a Shop Cart based the data in the body that is posted
    """
    app.logger.info("Request to create a Shop Cart")
    check_content_type("application/json")
    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())
    found_shop_cart = Shopcart.find_by_id(shopcart.id)
    logging.info("To create shopcart with id: %d", shopcart.id)
    if found_shop_cart is not None:
        logging.info("Found shopcart: %s", type(found_shop_cart))
        abort(status.HTTP_409_CONFLICT, f"Shopcart {shopcart.id} already exists")
    shopcart.create(id)
    message = Shopcart.find_by_id(shopcart.id).serialize()
    location_url = url_for("get_shopcarts", id=shopcart.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# LIST ALL PRODUCTS OF A GIVEN SHOP CART
######################################################################
@app.route("/shopcarts/<int:id>/products", methods=["GET"])
def list_products(id):
    """Return all of products of a given shopcart"""
    app.logger.info("Request for reading items of a given shop cart")
    shopcart = Shopcart().find_by_id(id)
    # If the shopcart does not exist, return 400 BAD REQUEST ERROR
    if not shopcart:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Shopcart with id '{id}' could not be found.",
        )
    results = [product.serialize() for product in shopcart.products]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE AN PRODUCT FROM SHOPCART
######################################################################
@app.route("/shopcarts/<int:id>/products/<int:product_id>", methods=["GET"])
def get_products(id, product_id):
    """
    Get an Address
    This endpoint returns just an address
    """
    app.logger.info(
        "Request to retrieve Product %s for CUSTOMER id: %s", (product_id, id)
    )

    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{product_id}' could not be found.",
        )

    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


######################################################################
# ADD A Product TO A shopcart
######################################################################
@app.route("/shopcarts/<int:id>/products", methods=["POST"])
def add_products(id):
    """
    Create a Product on a Shopcart
    This endpoint will add a product to a shopcart
    """
    app.logger.info("Request to create a Products for Shopcart with id: %s", id)
    check_content_type("application/json")

    shopcart = Shopcart().find_by_id(id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{id}' could not be found.",
        )

    product = Product()
    product.deserialize(request.get_json())
    shopcart.products.append(product)
    shopcart.update()
    message = product.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED)


######################################################################
# DELETE A Product
######################################################################
@app.route("/shopcarts/<int:id>/products/<int:product_id>", methods=["DELETE"])
def delete_products(id, product_id):
    """
    Delete a Product
    This endpoint will delete a Product based the id specified in the path
    """
    app.logger.info(
        "Request to delete Product %s for Customer id: %s", (product_id, id)
    )

    product = Product().find(product_id)
    if product:
        product.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# UPDATE A Product
######################################################################
@app.route(
    "/shopcarts/<int:id>/products/<int:product_id>",
    methods=["PUT"],
)
def update_products(id, product_id):
    """
    Update a Product
    This endpoint will update a product based the body that is posted
    """
    app.logger.info(
        "Request to update product %s for customer id: %s", (product_id, id)
    )
    check_content_type("application/json")

    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id '{product_id}' could not be found.",
        )

    product.deserialize(request.get_json())
    product.id = product_id
    product.update()
    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


######################################################################
# LIST ALL SHOP CARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """Returns all of the Shopcarts"""
    app.logger.info("Request for Shop Cart list")
    id = request.args.get("id")
    results = []
    if id:
        shopcarts = Shopcart.find_by_id(id)
        results = [shopcarts.serialize()]
    else:
        shopcarts = Shopcart.all()
        results = [shopcart.serialize() for shopcart in shopcarts]
    return make_response(jsonify(results), status.HTTP_200_OK)


@app.route("/shopcarts/<int:id>/clear", methods=["PUT"])
def clear_shopcarts(id):
    """Clear a shop cart according to customer id"""
    app.logger.info("Request to clear shop cart for customer id: %s", (id))
    check_content_type("application/json")

    shopcart = Shopcart.find_by_id(id)
    if not shopcart:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Shopcart with id '{id}' could not be found.",
        )
    for product in shopcart.products:
        product.delete()
    shopcart.products = []
    shopcart.id = id
    shopcart.update()
    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


######################################################################
# FILTER SHOP CARTS GIVEN A PRODUCT
######################################################################
@app.route(
    "/shopcarts/products/<string:product_name>",
    methods=["GET"],
)
def filter_shopcarts_by_product_name(product_name):
    """Return all shopcarts which contain the given product"""
    app.logger.info("Request for Shop Carts with given product")
    shopcarts = Shopcart.filter_by_product_name(product_name)
    results = [shopcart.serialize() for shopcart in shopcarts]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )


def init_db():
    """Initializes the SQLAlchemy app"""
    global app
    Shopcart.init_db(app)
