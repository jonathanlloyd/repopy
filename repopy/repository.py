"""Top-level classes and protocols for Repopy"""

from typing import (
    Any,
    Dict,
    Generic,
    List,
    Mapping,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
)

Field = Union[int, float, bool, str]

EntityType = TypeVar('EntityType')
FilterType = TypeVar('FilterType', contravariant=True)
UpdatesType = TypeVar('UpdatesType', contravariant=True)


class RepositoryProtocol(Protocol, Generic[EntityType, FilterType, UpdatesType]):
    """Top-level protocol for the repository. Application code that depends on
    the repository should use this type"""

    def add(self, entity: EntityType):
        """Insert a new record into the repository"""

    def query(self, filters: FilterType, limit: int=None) -> List[EntityType]:
        """Return the records in the repository that match the given filters
        (up to the limit, if given)"""

    def update(self, updates: UpdatesType, filters: FilterType) -> int:
        """Update the provided fields on all records that match the given
        filters"""

    def delete(self, filters: FilterType) -> int:
        """Remove all records from the repository that match the given filter"""


class BackendProtocol(Protocol, Generic[EntityType]):
    """Interface that must be implemented by storage backends for Repopy
    repositories"""

    def add(self, entity: EntityType):
        """Store a new record via this backend"""

    def query(
        self,
        filters: Mapping[str, Field],
        limit: Optional[int],
    ) -> List[EntityType]:
        """Query this backend for any records that match the provided filters
        (up to the limit, if provided)"""

    def update(
        self,
        updates: Mapping[str, Field],
        filters: Mapping[str, Field],
    ) -> int:
        """Update the provided fields on the records in this backend that
        match the given filters"""

    def delete(self, filters: Mapping[str, Field]) -> int:
        """Delete the records in this backend that match the given filters"""


class Repository(Generic[EntityType, FilterType, UpdatesType]):
    """Default implementation of the repopy Repository Protocol"""

    _backend: BackendProtocol
    _field_names: List[str]

    def __init__(self, backend, field_names):
        self._backend = backend
        self._field_names = field_names

    def add(self, entity: EntityType):
        """Insert a new record into the repository"""
        self._backend.add(entity)

    def query(self, filters: FilterType, limit: int=None) -> List[EntityType]:
        """Return the records in the repository that match the given filters
        (up to the limit, if given)"""
        field_map = self._to_field_map(filters)
        return self._backend.query(field_map, limit)

    def update(self, updates: UpdatesType, filters: FilterType) -> int:
        """Update the provided fields on all records that match the given
        filters"""

    def delete(self, filters: FilterType) -> int:
        """Remove all records from the repository that match the given filter"""

    def _to_field_map(self, obj: Any) -> Mapping[str, Field]:
        field_map = {}
        for field_name in self._field_names:
            if getattr(obj, field_name, None) is not None:
                field_map[field_name] = getattr(obj, field_name)
        return field_map


class RepositoryFactory(Generic[EntityType, FilterType, UpdatesType]): # pylint: disable=too-few-public-methods
    """Static methods for creating valid repositories"""

    @staticmethod
    def create_repository(
        entity_cls: Type[EntityType],
        _filter_cls: Type[FilterType],
        _updates_cls: Type[UpdatesType],
        backend: BackendProtocol,
    ) -> Repository[EntityType, FilterType, UpdatesType]:
        """Create a new repository with the provided types and backend"""
        fields: Dict[str, Field] = {}
        for field_name, field_type in entity_cls.__annotations__.items():
            fields[field_name] = field_type
#        fields: Dict[str, Field] = {}
#        for field_name, field_type in entity_cls.__annotations__.items():
#            if field_type not in Field.__args__:
#                raise ValueError(f'Field type \"{field_type}\" not supported')
#            fields[field_name] = field_type
#
#        for field_name, field_type in filter_cls.__annotations__.items():
#            if fields.get(field_name) != field_type:
#                raise ValueError(f'Field \"{field_name}\" in filter class does not match entity')
#
#        for field_name, field_type in updates_cls.__annotations__.items():
#            if fields.get(field_name) != field_type:
#                raise ValueError(f'Field \"{field_name}\" in updates class does not match entity')

        return Repository(backend, list(fields.keys()))
