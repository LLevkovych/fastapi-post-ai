from loguru import logger

# Configure logger
logger.add("app.log", rotation="10 MB", level="INFO")
