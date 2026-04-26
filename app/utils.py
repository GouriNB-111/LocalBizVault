import re

def generate_slug(name):
    return re.sub(r'\W+', '-', name.lower())