import os
import random
import string
from django.utils.text import slugify

def upload_to_path(instance, filename, base_path='uploads'):
    """
    Generate file upload path: base_path/model_name/filename
    """
    model_name = instance.__class__.__name__.lower()
    return os.path.join(base_path, model_name, filename)

def random_string(length=12):
    """
    Generate a random alphanumeric string of given length.
    """
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def slugify_string(value):
    """
    Slugify a string value.
    """
    return slugify(value)

PAGINATION_DEFAULTS = {
    'PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
}
