from typing import (
    Generic,
    List,
    Protocol,
    TypeVar,
    Union,
)

EntityType = TypeVar('EntityType')
FilterType = TypeVar('FilterType', contravariant=True)
UpdatesType = TypeVar('UpdatesType', contravariant=True)


class Repository(Protocol, Generic[EntityType, FilterType, UpdatesType]):
    def add(self, entity: EntityType):
        pass

    def query(self, filters: FilterType, limit: int=None) -> List[EntityType]:
        pass

    def update(self, updates: UpdatesType, filters: FilterType) -> int:
        pass

    def delete(self, filters: FilterType) -> int:
        pass
