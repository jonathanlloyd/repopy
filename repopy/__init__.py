"""Interface (and default implementation set)
for the Repository Pattern in Python"""

from .repository import BackendProtocol, RepositoryFactory, Repository, RepositoryProtocol

__version__ = '0.1.0'

__all__ = [
    'Repository',
]