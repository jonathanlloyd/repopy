"""In-memory generic implementation of the repository protocol"""

from typing import (
    Generic,
    List,
)

from ..repository import (
    EntityType,
    FilterType,
    UpdatesType,
)


class InMemory(Generic[EntityType, FilterType, UpdatesType]):
    _entity_store: List[EntityType]

    def __init__(self):
        self._entity_store = []

    def add(self, entity: EntityType):
        self._entity_store.append(entity)

    def query(self, filters: FilterType, limit: int=None) -> List[EntityType]:
        filters_dict = self._get_filters_dict(filters)
        return [
            entity
            for entity in self._entity_store
            if all([
                getattr(entity, filter_name) == filter_value
                for filter_name, filter_value in filters_dict.items()
            ])
        ]

    def update(self, updates: UpdatesType, filters: FilterType) -> int:
        pass

    def delete(self, filters: FilterType) -> int:
        pass

    @staticmethod
    def _get_filters_dict(filters: FilterType):
        filter_names = list(filters.__annotations__.keys())
        return {
            filter_name: getattr(filters, filter_name)
            for filter_name in filter_names
            if getattr(filters, filter_name) is not None
        }
