"""Top-level classes and protocols for Repopy"""

from typing import (
    Any,
    Generic,
    List,
    Mapping,
    Protocol,
)

from .backend import BackendProtocol
from .middleware import RepositoryMiddleware
from .types import (
    Field,
    EntityType,
    FilterType,
    UpdatesType,
)


class RepositoryProtocol(Protocol, Generic[EntityType, FilterType, UpdatesType]):
    """Top-level protocol for the repository. Application code that depends on
    the repository should use this type"""

    def with_middleware(
        self,
        middleware: RepositoryMiddleware[EntityType, FilterType, UpdatesType],
    ) -> "RepositoryProtocol[EntityType, FilterType, UpdatesType]":
        """Construct a new repository wrapped with the provided middlware"""

    def add(self, entities: List[EntityType]):
        """Insert one or more new records into the repository"""

    def query(self, filters: FilterType, limit: int = None) -> List[EntityType]:
        """Return the records in the repository that match the given filters
        (up to the limit, if given)"""

    def update(self, updates: UpdatesType, filters: FilterType) -> int:
        """Update the provided fields on all records that match the given
        filters"""

    def delete(self, filters: FilterType) -> int:
        """Remove all records from the repository that match the given filter"""


class Repository(Generic[EntityType, FilterType, UpdatesType]):
    """Default implementation of the repopy Repository Protocol"""

    _backend: BackendProtocol
    _middleware: List[RepositoryMiddleware]
    _field_names: List[str]

    def __init__(
        self,
        backend: BackendProtocol,
        field_names: List[str],
        middleware: List[RepositoryMiddleware] = None,
    ) -> None:
        self._backend = backend
        self._field_names = field_names
        self._middleware = middleware or []

    def with_middleware(
        self,
        middleware: RepositoryMiddleware[EntityType, FilterType, UpdatesType],
    ) -> RepositoryProtocol[EntityType, FilterType, UpdatesType]:
        """Construct a new repository wrapped with the provided middlware"""
        repo = Repository[EntityType, FilterType, UpdatesType](
            self._backend,
            self._field_names,
            self._middleware + [middleware],
        )
        return repo

    def add(self, entities: List[EntityType]):
        """Insert one or more new records into the repository"""
        def compose(middleware_add, next_func):
            def add(entities):
                return middleware_add(entities, next_func)
            return add

        add_func = self._backend.add
        for middleware in self._middleware:
            add_func = compose(middleware.add, add_func)

        return add_func(entities)

    def query(self, filters: FilterType, limit: int=None) -> List[EntityType]:
        """Return the records in the repository that match the given filters
        (up to the limit, if given)"""
        field_map = self._to_field_map(filters)

        def compose(middleware_query, next_func):
            def query(filters, limit):
                return middleware_query(
                    filters=filters,
                    limit=limit,
                    next_func=next_func,
                )
            return query

        query_func = self._backend.query
        for middleware in self._middleware:
            query_func = compose(middleware.query, query_func)

        return query_func(field_map, limit)

    def update(self, updates: UpdatesType, filters: FilterType) -> int:
        """Update the provided fields on all records that match the given
        filters"""

        def compose(middleware_update, next_func):
            def update(updates, filters) -> int:
                return middleware_update(updates, filters, next_func)
            return update

        def update_func(updates: UpdatesType, filters: FilterType) -> int:
            updates_map = self._to_field_map(updates)
            filters_map = self._to_field_map(filters)
            return self._backend.update(updates_map, filters_map)

        for middleware in self._middleware:
            update_func = compose(middleware.update, update_func)

        return update_func(updates, filters)

    def delete(self, filters: FilterType) -> int:
        """Remove all records from the repository that match the given filter"""

        def compose(middleware_delete, next_func):
            def delete(filters):
                return middleware_delete(filters, next_func)
            return delete

        def delete_func(filters: FilterType) -> int:
            filters_map = self._to_field_map(filters)
            return self._backend.delete(filters_map)

        for middleware in self._middleware:
            delete_func = compose(middleware.delete, delete_func)

        return delete_func(filters)

    def _to_field_map(self, obj: Any) -> Mapping[str, Field]:
        field_map = {}
        for field_name in self._field_names:
            if getattr(obj, field_name, None) is not None:
                field_map[field_name] = getattr(obj, field_name)
        return field_map
