import logging

logger = None

def initLogger(output_path):
    # Set up the logger
    global logger

    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    # Create a handler for terminal output (stdout)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    # Create a handler for log file output
    file_handler = logging.FileHandler(output_path)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and attach it to both handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
