import dataclasses
from dataclasses import dataclass
from typing import Dict, Optional

import pytest # type: ignore

from repopy import BackendProtocol, RepositoryFactory
from repopy.backends import InMemory


@dataclass
class BadType:
    id: str
    count: int
    bad_field: Dict[str, str]

@dataclass
class BadTypeFilter:
    count: Optional[int]

@dataclass
class BadTypeUpdate:
    count: Optional[int]


@dataclass
class SomeType:
    id: str
    count: int

@dataclass
class SomeTypeFilter:
    count: Optional[int]

@dataclass
class SomeTypeUpdate:
    count: Optional[int]


def setup_in_memory_backend() -> BackendProtocol[SomeType]:
    def copy_func(entity: SomeType) -> SomeType:
        return SomeType(**dataclasses.asdict(entity))
    return InMemory(copy_func)


@pytest.fixture(params=[setup_in_memory_backend])
def backend(request):
    return request.param()


def test_unsupported_field_type(backend: BackendProtocol[BadType]):
    with pytest.raises(ValueError) as e:
         RepositoryFactory.create_repository(
            BadType,
            BadTypeFilter,
            BadTypeUpdate,
            backend,
        )

    assert str(e.value) == 'Field type "typing.Dict[str, str]" not supported'


def test_incompatible_filter_type(backend: BackendProtocol[SomeType]):
    # When a repository is created with a filter field not in the entity type
    @dataclass
    class BadFilterBogusField:
        not_count: Optional[int]

    with pytest.raises(ValueError) as e:
        RepositoryFactory.create_repository(
            SomeType,
            BadFilterBogusField,
            SomeTypeUpdate,
            backend,
        )

    # Then a ValueError should be raised
    assert str(e.value) == \
        'Filter type not compatible: field "not_count" not in entity type'

    # When a repository is created with a filter field with a type that does
    # not match the field in the entity type
    @dataclass
    class BadFilterWrongType:
        count: Optional[bool]

    with pytest.raises(ValueError) as e:
        RepositoryFactory.create_repository(
            SomeType,
            BadFilterWrongType,
            SomeTypeUpdate,
            backend,
        )

    # Then a ValueError should be raised
    assert str(e.value) == \
        (
            'Filter type not compatible: field "count" should have type '
            + '<class \'int\'>/typing.Union[int, NoneType]'
        )


def test_incompatible_update_type(backend: BackendProtocol[SomeType]):
    # When a repository is created with an update field not in the entity type
    @dataclass
    class BadUpdateBogusField:
        not_count: Optional[int]

    with pytest.raises(ValueError) as e:
        RepositoryFactory.create_repository(
            SomeType,
            SomeTypeFilter,
            BadUpdateBogusField,
            backend,
        )

    # Then a ValueError should be raised
    assert str(e.value) == \
        'Update type not compatible: field "not_count" not in entity type'

    # When a repository is created with a filter field with a type that does
    # not match the field in the entity type
    @dataclass
    class BadUpdateWrongType:
        count: Optional[bool]

    with pytest.raises(ValueError) as e:
        RepositoryFactory.create_repository(
            SomeType,
            SomeTypeFilter,
            BadUpdateWrongType,
            backend,
        )

    # Then a ValueError should be raised
    assert str(e.value) == \
        (
            'Update type not compatible: field "count" should have type '
            + '<class \'int\'>/typing.Union[int, NoneType]'
        )
