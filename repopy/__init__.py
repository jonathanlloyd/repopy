"""Interface (and default implementation set)
for the Repository Pattern in Python"""

from .repository import (
    BackendProtocol,
    RepositoryFactory,
    RepositoryProtocol,
)

__version__ = '0.1.3'

__all__ = [
    'BackendProtocol',
    'RepositoryFactory',
    'RepositoryProtocol',
]
