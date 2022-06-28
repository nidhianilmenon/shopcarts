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
    """Root URL response"""
    return (
        jsonify(
            name="Shop Cart REST API Service",
            version="1.0",
            paths=url_for("list_shopcarts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# TEST INTERVAL SERVER ERROR
######################################################################
@app.route("/test_internal_server_error", methods=["POST"])
def test_internal_server_error():
    """Route for testing internal server error"""
    abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "Test for internal server error")


######################################################################
# RETRIEVE AN ACCOUNT
# RETRIEVE A SHOP CART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>", methods=["GET"])
def get_shopcarts(shopcart_id):
    """
    Retrieve a shopcart of a customer
    This endpoint will return a shopcart based on it's id
    """
    app.logger.info("Request for Shopcart with id: %s", shopcart_id)
    shopcart = Shopcart.find(shopcart_id)
    if not shopcart:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )

    return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)


######################################################################
# CREATE A NEW SHOP CART
######################################################################
@app.route("/shopcarts", methods=["POST"])
def create_shopcarts():
    """
    Creates a Shopcart
    This endpoint will create a Shop Cart based the data in the body that is posted
    """
    app.logger.info("Request to create a Shop Cart")
    check_content_type("application/json")
    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())
    found_shop_cart = Shopcart.find_by_customer_id(shopcart.customer_id)
    logging.info("To create shopcart with customer_id: %d", shopcart.customer_id)
    if found_shop_cart is not None:
        logging.info("Found shopcart: %s", type(found_shop_cart))
        abort(status.HTTP_409_CONFLICT, f"Shopcart {shopcart.customer_id} already exists")
    shopcart.create()
    message = Shopcart.find(shopcart.id).serialize()
    location_url = url_for("get_shopcarts", shopcart_id=shopcart.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# ADD A NEW PRODUCT
######################################################################
@app.route("/product", methods=["POST"])
def add_product():
    """
    Add a Product to a existed Shopcart
    This endpoint will add a product to a given shopcart based on the posted data in the body
    """
    app.logger.info("Request to add a Product to a Shop Cart")
    check_content_type("application/json")
    product = Product()
    product.deserialize(request.get_json())
    Shopcart.add_product(product)
    shopCart = Shopcart.find(product.shopcart_id)
    message = shopCart.serialize()
    location_url = url_for("add_product", shopcart_id=shopCart.id, _external=True)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# DELETE A PRODUCT FROM A SHOP CART
######################################################################
@app.route("/product", methods=["DELETE"])
def delete_product():
    """Delete a product from existing shopcart
    Returns:
    The shopcart json data after deletion
    """
    app.logger.info("Request to delete a Product from a Shop Cart")
    check_content_type("application/json")
    product = Product()
    product.deserialize(request.get_json())
    shopCart = Shopcart.find(product.shopcart_id)
    Shopcart.delete_item(shopCart.customer_id, product.id)
    location_url = url_for("delete_product", shopcart_id=shopCart.id, _external=True)
    return make_response(
        "", status.HTTP_204_NO_CONTENT, {"Location": location_url}
    )


######################################################################
# LIST ALL SHOP CARTS
######################################################################
@app.route("/shopcarts", methods=["GET"])
def list_shopcarts():
    """Returns all of the Shopcarts"""
    app.logger.info("Request for Shop Cart list")
    customer_id = request.args.get("customer_id")
    results = []
    if customer_id:
        shopcarts = Shopcart.find_by_customer_id(customer_id)
        results = [shopcarts.serialize()]
    else:
        shopcarts = Shopcart.all()
        results = [shopcart.serialize() for shopcart in shopcarts]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# LIST ALL PRODUCTS OF A GIVEN SHOP CART
######################################################################
@app.route("/shopcarts/<int:shopcart_id>/product", methods=["GET"])
def get_products(shopcart_id):
    """Return all of products of a given shopcart"""
    app.logger.info("Request for reading items of a given shop cart")
    shopcart = Shopcart.find(shopcart_id)
    # If the shopcart does not exist, return 400 BAD REQUEST ERROR
    if not shopcart:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Shopcart with id '{shopcart_id}' could not be found.",
        )
    products = Shopcart.read_items(shopcart.customer_id)
    message = jsonify([product.serialize() for product in products])
    return make_response(message, status.HTTP_200_OK)


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
