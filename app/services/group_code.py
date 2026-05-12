import random
import string


def generate_group_code() -> str:
    def segment(length: int) -> str:
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    return f"{segment(10)}"

def update_group(name, description):
    if name:
        name