"""Interface (and default implementation set) for the Repository Pattern in
Python"""

from .backend import BackendProtocol
from .middleware import (
    RepositoryMiddleware,
    AddMethodType,
    QueryMethodType,
    UpdateMethodType,
    DeleteMethodType,
)
from .repository import RepositoryProtocol
from .repositoryfactory import RepositoryFactory


__all__ = [
    'BackendProtocol',
    'RepositoryFactory',
    'RepositoryMiddleware',
    'AddMethodType',
    'QueryMethodType',
    'UpdateMethodType',
    'DeleteMethodType',
    'RepositoryProtocol',
]
