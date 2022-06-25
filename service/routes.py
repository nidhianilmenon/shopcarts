"""
My Service

Describe what your service does here
"""

# from flask import Flask, jsonify, request, url_for, make_response, abort
from .utils import status  # HTTP Status Codes
from service.models import Shopcart

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def init_db():
    """Initializes the SQLAlchemy app"""
    global app
    Shopcart.init_db(app)
