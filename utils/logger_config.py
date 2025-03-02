import logging
import os

# Create a logger
logger = logging.getLogger("my_app")
logger.setLevel(logging.DEBUG)

# Create a file handler which logs even debug messages
log_filename = os.path.join(os.getcwd(), "debug.log")
fh = logging.FileHandler(log_filename)
fh.setLevel(logging.DEBUG)

# Create a console handler (optional)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
