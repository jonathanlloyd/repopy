import dataclasses
from dataclasses import dataclass
from typing import Dict, Optional, Type

import pytest # type: ignore

from repopy import BackendProtocol, RepositoryFactory, RepositoryProtocol
from repopy.backends import InMemory


@dataclass
class Person:
    id: str
    name: str
    age: int

@dataclass
class PersonFilter:
    name: Optional[str] = None
    age: Optional[int] = None

@dataclass
class PersonUpdate:
    name: Optional[str] = None


def setup_in_memory_backend() -> BackendProtocol[Person]:
    def copy_func(person: Person) -> Person:
        return Person(**dataclasses.asdict(person))
    return InMemory(copy_func)

@pytest.fixture(params=[setup_in_memory_backend])
def backend(request):
    return request.param()


def test_unsupported_field_type(backend: BackendProtocol[Person]):
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

    with pytest.raises(ValueError) as e:
        repository = RepositoryFactory.create_repository(
            BadType,
            BadTypeFilter,
            BadTypeUpdate,
            backend,
        )

    assert str(e.value) == 'Field type "typing.Dict[str, str]" not supported'


def test_incompatible_filter_type(backend: BackendProtocol[Person]):
    # Given some domain types
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


def test_incompatible_update_type(backend: BackendProtocol[Person]):
    # Given some domain types
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


def test_add(backend: BackendProtocol[Person]):
    # Given a repository
    person_repository = RepositoryFactory.create_repository(
        Person,
        PersonFilter,
        PersonUpdate,
        backend,
    )

    # And several test records
    persons = []
    for i in range(0, 5):
        test_person = Person(
            id=f'person-{i}',
            name=f'name-{i}',
            age=50,
        )
        persons.append(test_person)

    # When add is called
    person_repository.add(persons)

    # Then all inserted records should be returned when queried
    queried_persons = person_repository.query(PersonFilter(
        age=50,
    ))

    assert len(queried_persons) == 5, \
        "Expected all inserted records to be returned"
    for person in persons:
        assert person in queried_persons, \
            'Expected "{person.id}" to have been stored, but it wasn\'t'


def test_query(backend: BackendProtocol[Person]):
    # Given a repository
    person_repository = RepositoryFactory.create_repository(
        Person,
        PersonFilter,
        PersonUpdate,
        backend,
    )

    # In which several records have been inserted
    test_persons = []
    for i in range(0, 10):
        test_person = Person(
            id=f'person-{i}',
            name=f'name-{i}',
            age=25, # 25 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    for i in range(10, 20):
        test_person = Person(
            id=f'person-{i}',
            name=f'name-{i}',
            age=50 # 50 yrs old,
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    # When a subset of records are queried
    query_set = [p.id for p in test_persons[:5]]
    queried_persons = person_repository.query(PersonFilter(
        age=50,
    ))

    # Then those records, and only those records, should be returned
    assert len(queried_persons) == 10, \
        f'Expected 10 records to be returned, got {len(queried_persons)}'
    for person in test_persons[10:]:
        assert person in queried_persons, \
            f'Expected "{person.id}" to be in results, but it wasn\'t'


def test_query_obeys_limit(backend: BackendProtocol[Person]):
    # Given a repository
    person_repository = RepositoryFactory.create_repository(
        Person,
        PersonFilter,
        PersonUpdate,
        backend,
    )

    # In which several records have been inserted
    test_persons = []
    for i in range(0, 10):
        test_person = Person(
            id=f'person-{i}',
            name=f'name-{i}',
            age=25, # 25 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    # When queried with a limit < the number of records
    queried_persons = person_repository.query(PersonFilter(), limit=5)

    # Then the number of records returned should be equal to the limit
    assert len(queried_persons) == 5, \
        f'Expected 5 records to be returned, got {len(queried_persons)}'


def test_query_handles_large_limit(backend: BackendProtocol[Person]):
    # Given a repository
    person_repository = RepositoryFactory.create_repository(
        Person,
        PersonFilter,
        PersonUpdate,
        backend,
    )

    # In which several records have been inserted
    test_persons = []
    for i in range(0, 10):
        test_person = Person(
            id=f'person-{i}',
            name=f'name-{i}',
            age=25, # 25 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    # When queried with a limit > the number of records
    queried_persons = person_repository.query(PersonFilter(), limit=50)

    # Then the number of records returned should be equal to the total
    # number of records
    assert len(queried_persons) == 10, \
        f'Expected 10 records to be returned, got {len(queried_persons)}'


def test_update(backend: BackendProtocol[Person]):
    # Given a repository
    person_repository = RepositoryFactory.create_repository(
        Person,
        PersonFilter,
        PersonUpdate,
        backend,
    )

    # In which several records have been inserted
    test_persons = []
    for i in range(0, 10):
        test_person = Person(
            id=f'person-{i}',
            name=f'name-{i}',
            age=25, # 25 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    for i in range(10, 20):
        test_person = Person(
            id=f'person-{i}',
            name=f'name-{i}',
            age=50, # 50 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    # When some of them are updated
    num_updated = person_repository.update(
        PersonUpdate(
            name='new-name',
        ),
        PersonFilter(
            age=25,
        ),
    )

    # Then the count of updated records should be correct
    assert num_updated == 10

    # And the records that match the update should have been changed
    updated_records = person_repository.query(PersonFilter(
        age=25,
    ))
    assert len(updated_records) == 10
    assert all([
        person.name == 'new-name'
        for person in updated_records
    ]), 'All matching records should have been updated'

    # And those that don't should be unaltered
    not_updated_records = person_repository.query(PersonFilter(
        age=50,
    ))
    assert len(not_updated_records) == 10
    assert all([
        person.name != 'new-name'
        for person in not_updated_records
    ]), 'Non-matching records should be unaltered'


def test_delete(backend: BackendProtocol[Person]):
    # Given a repository
    person_repository = RepositoryFactory.create_repository(
        Person,
        PersonFilter,
        PersonUpdate,
        backend,
    )

    # In which several records have been inserted
    test_persons = []
    for i in range(0, 10):
        test_person = Person(
            id=f'person-{i}',
            name=f'name-{i}',
            age=25, # 25 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    for i in range(10, 20):
        test_person = Person(
            id=f'person-{i}',
            name=f'name-{i}',
            age=50, # 50 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    # When some of them are deleted
    num_deleted = person_repository.delete(
        PersonFilter(
            age=25,
        ),
    )

    # Then the count of deleted records should be correct
    assert num_deleted == 10

    # And the records that match the update should have been removed
    deleted_records = person_repository.query(PersonFilter(
        age=25,
    ))
    assert len(deleted_records) == 0

    # And those that don't should be left
    not_deleted_records = person_repository.query(PersonFilter(
        age=50,
    ))
    assert len(not_deleted_records) == 10
