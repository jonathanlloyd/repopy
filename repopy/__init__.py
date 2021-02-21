"""Interface (and default implementation set)
for the Repository Pattern in Python"""

from .backend import BackendProtocol
from .repository import RepositoryProtocol
from .repositoryfactory import RepositoryFactory

__all__ = [
    'BackendProtocol',
    'RepositoryFactory',
    'RepositoryProtocol',
]
