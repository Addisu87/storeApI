import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Choose the desired logging level (DEBUG, INFO, ERROR, etc.)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
)

# Create a logger instance
logger = logging.getLogger(__name__)
