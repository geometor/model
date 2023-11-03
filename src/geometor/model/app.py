"""
run the main app
"""
from .model import Model


def run() -> None:
    reply = Model().run()
    print(reply)
