"""Allows access to submodules from dfi.<module>"""
from importlib.metadata import version

__version__ = version("dfipy")

from .client import Client
