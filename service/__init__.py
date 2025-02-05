"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import sys
from flask import Flask
from service import config
from .utils import log_handlers

# Create Flask application
app = Flask(__name__)

# Load Configurations
app.config.from_object(config)

# Dependencies require we import the routes AFTER the Flask app is created
# pylint: disable=wrong-import-position, wrong-import-order
from service import routes  # noqa: E402, E261

# pylint: disable=wrong-import-position
from .utils import error_handlers, cli_commands  # noqa: F401 E402

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    routes.init_db()  # make our SQLAlchemy tables
except Exception as error:
    app.logger.critical("%s: Cannot continue", error)
    # gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

app.logger.info("Service initialized!")
