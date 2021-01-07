"""Interface (and default implementation set)
for the Repository Pattern in Python"""

from .repository import (
    BackendProtocol,
    RepositoryFactory,
    RepositoryProtocol,
)

__all__ = [
    'BackendProtocol',
    'RepositoryFactory',
    'RepositoryProtocol',
]
