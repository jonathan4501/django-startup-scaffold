import logging
import sys

LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format=LOGGING_FORMAT,
        stream=sys.stdout,
    )
    logging.getLogger('django').setLevel(logging.WARNING)
    logging.getLogger('django.db.backends').setLevel(logging.WARNING)
