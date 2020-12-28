"""Interface (and default implementation set)
for the Repository Pattern in Python"""

from .repository import (
    BackendProtocol as BackendProtocol,
    RepositoryFactory as RepositoryFactory,
    RepositoryProtocol as RepositoryProtocol,
)

__version__ = '0.1.0'

__all__ = [
    'BackendProtocol',
    'RepositoryFactory',
    'RepositoryProtocol',
]
