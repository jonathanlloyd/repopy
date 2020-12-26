"""In-memory generic implementation of the repository protocol"""
# pylint: disable=missing-function-docstring

from typing import (
    Callable,
    Generic,
    List,
    Mapping,
    Optional,
)

from ..repository import (
    EntityType,
    Field,
)


class InMemory(Generic[EntityType]):
    """In-memory backend for Repopy. Useful for testing applications without
    relying on an external database"""

    _copy_func: Optional[Callable[[EntityType], EntityType]]
    _entity_store: List[EntityType]

    def __init__(self, copy_func: Callable[[EntityType], EntityType]):
        self._copy_func = copy_func
        self._entity_store = []

    def add(self, entity: EntityType):
        if self._copy_func:
            self._entity_store.append(self._copy_func(entity))

    def query(
        self,
        filters: Mapping[str, Field],
        limit: Optional[int],
    ) -> List[EntityType]:
        matching_entities = [
            entity
            for entity in self._entity_store
            if all([
                getattr(entity, filter_name) == filter_value
                for filter_name, filter_value in filters.items()
            ])
        ]

        if limit is not None and limit < len(matching_entities):
            return matching_entities[:limit]
        return matching_entities

    def update(
        self,
        updates: Mapping[str, Field],
        filters: Mapping[str, Field],
    ) -> int:
        pass

    def delete(self, filters: Mapping[str, Field]) -> int:
        pass
