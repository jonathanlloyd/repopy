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

    def add(self, entities: List[EntityType]):
        assert self._copy_func is not None
        for entity in entities:
            self._entity_store.append(self._copy_func(entity))

    def query(
        self,
        filters: Mapping[str, Field],
        limit: Optional[int],
    ) -> List[EntityType]:
        matching_entities = [
            entity
            for entity in self._entity_store
            if self._matches(filters, entity)
        ]

        if limit is not None and limit < len(matching_entities):
            return matching_entities[:limit]
        return matching_entities

    def update(
        self,
        updates: Mapping[str, Field],
        filters: Mapping[str, Field],
    ) -> int:
        num_updated = 0
        new_entities = []
        for entity in self._entity_store:
            if self._matches(filters, entity):
                new_entities.append(self._apply_updates(updates, entity))
                num_updated += 1
            else:
                new_entities.append(entity)
        self._entity_store = new_entities
        return num_updated

    def delete(self, filters: Mapping[str, Field]) -> int:
        num_deleted = 0
        new_entities = []
        for entity in self._entity_store:
            if self._matches(filters, entity):
                num_deleted += 1
            else:
                new_entities.append(entity)
        self._entity_store = new_entities
        return num_deleted

    def _matches(self, filters: Mapping[str, Field], entity: EntityType): # pylint: disable=no-self-use
        return all([
            getattr(entity, filter_name) == filter_value
            for filter_name, filter_value in filters.items()
        ])

    def _apply_updates(self, updates, entity):
        assert self._copy_func is not None
        new_entity = self._copy_func(entity)
        for field_name, new_value in updates.items():
            setattr(new_entity, field_name, new_value)
        return new_entity
