from typing import (
    Generic,
    Type,
    Dict,
    Optional,
    List,
    Mapping,
    Protocol,
    TypeVar,
    Union,
    get_args,
    Any,
)

Field = Union[int, float, bool, str]

EntityType = TypeVar('EntityType')
FilterType = TypeVar('FilterType', contravariant=True)
UpdatesType = TypeVar('UpdatesType', contravariant=True)


class RepositoryProtocol(Protocol, Generic[EntityType, FilterType, UpdatesType]):
    def add(self, entity: EntityType):
        pass

    def query(self, filters: FilterType, limit: int=None) -> List[EntityType]:
        pass

    def update(self, updates: UpdatesType, filters: FilterType) -> int:
        pass

    def delete(self, filters: FilterType) -> int:
        pass


class BackendProtocol(Protocol, Generic[EntityType]):
    def add(self, entity: EntityType):
        pass

    def query(self, filters: Mapping[str, Field], limit: Optional[int]) -> List[EntityType]:
        pass

    def update(self, updates: Mapping[str, Field], filters: Mapping[str, Field]) -> int:
        pass

    def delete(self, filters: Mapping[str, Field]) -> int:
        pass


class Repository(Generic[EntityType, FilterType, UpdatesType]):
    _backend: BackendProtocol
    _field_names: List[str]

    def __init__(self, backend, field_names):
        self._backend = backend
        self._field_names = field_names

    def add(self, entity: EntityType):
        self._backend.add(entity)

    def query(self, filters: FilterType, limit: int=None) -> List[EntityType]:
        field_map = self._to_field_map(filters)
        return self._backend.query(field_map, limit)

    def update(self, updates: UpdatesType, filters: FilterType) -> int:
        pass

    def delete(self, filters: FilterType) -> int:
        pass

    def _to_field_map(self, o: Any) -> Mapping[str, Field]:
        field_map = {}
        for field_name in self._field_names:
            if getattr(o, field_name, None) is not None:
                field_map[field_name] = getattr(o, field_name)
        return field_map


class RepositoryFactory(Generic[EntityType, FilterType, UpdatesType]):
    @staticmethod
    def create_repository(
        entity_cls: Type[EntityType],
        filter_cls: Type[FilterType],
        updates_cls: Type[UpdatesType],
        backend: BackendProtocol,
    ) -> Repository[EntityType, FilterType, UpdatesType]:
        fields: Dict[str, Field] = {}
        for field_name, field_type in entity_cls.__annotations__.items():
            fields[field_name] = field_type
        """
        fields: Dict[str, Field] = {}
        for field_name, field_type in entity_cls.__annotations__.items():
            if field_type not in Field.__args__:
                raise ValueError(f'Field type \"{field_type}\" not supported')
            fields[field_name] = field_type

        for field_name, field_type in filter_cls.__annotations__.items():
            if fields.get(field_name) != field_type:
                raise ValueError(f'Field \"{field_name}\" in filter class does not match entity')

        for field_name, field_type in updates_cls.__annotations__.items():
            if fields.get(field_name) != field_type:
                raise ValueError(f'Field \"{field_name}\" in updates class does not match entity')
        """

        return Repository(backend, list(fields.keys()))
