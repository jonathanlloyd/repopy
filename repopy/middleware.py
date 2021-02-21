"""Base class for repository middlewares"""

from typing import (
    Callable,
    Generic,
    List,
    Optional,
)

from .types import (
    EntityType,
    FilterType,
    UpdatesType,
)


AddMethodType = Callable[
    [List[EntityType]],
    None,
]
QueryMethodType = Callable[
    [FilterType, Optional[int]],
    List[EntityType],
]
UpdateMethodType = Callable[
    [UpdatesType, FilterType],
    int,
]
DeleteMethodType = Callable[
    [FilterType],
    int,
]


# pylint: disable=no-self-use
class RepositoryMiddleware(Generic[EntityType, FilterType, UpdatesType]):
    """Allows custom logic to be associated with a given repository.

    Example:
        class MiddlwareLogQueries(RepositoryMiddleware):
            def query(filters, next_func, limit = None):
                print(filters, limit)
                return next_func(filters, limit)

        some_repository = some_repository.with_middleware(MiddlwareLogQueries())
    """

    def add(
        self,
        entities: List[EntityType],
        next_func: AddMethodType[EntityType],
    ):
        """Override this method to intercept calls to the add method on the
        underlying repository"""
        return next_func(entities)

    def query(
        self,
        filters: FilterType,
        next_func: QueryMethodType[FilterType, EntityType],
        limit: int = None,
    ) -> List[EntityType]:
        """Override this method to intercept calls to the query method on the
        underlying repository"""
        return next_func(filters, limit)

    def update(
        self,
        updates: UpdatesType,
        filters: FilterType,
        next_func: UpdateMethodType[UpdatesType, FilterType],
    ) -> int:
        """Override this method to intercept calls to the update method on the
        underlying repository"""
        return next_func(updates, filters)

    def delete(
        self,
        filters: FilterType,
        next_func: DeleteMethodType[FilterType],
    ) -> int:
        """Override this method to intercept calls to the delete method on the
        underlying repository"""
        return next_func(filters)
