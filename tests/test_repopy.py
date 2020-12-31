import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type, TypeVar

import pytest # type: ignore
from sqlalchemy import create_engine, MetaData # type: ignore

from repopy import BackendProtocol, RepositoryFactory
from repopy.backends import InMemory, SQLAlchemy
from repopy.backends.sqlalchemy import type_safe_get


@dataclass
class Person:
    person_id: str
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

def setup_sqlalchemy_backend() -> BackendProtocol[Person]:
    class PersonCodec:
        @staticmethod
        def to_dict(person: Person) -> Dict[str, Any]:
            return {
                'id': person.person_id,
                'full_name': person.name,
                'age': person.age,
            }

        @staticmethod
        def from_dict(data: Dict[str, Any]) -> Person:
            return Person(
                person_id=type_safe_get(data, 'id', str),
                name=type_safe_get(data, 'full_name', str),
                age=type_safe_get(data, 'age', int),
            )

        @staticmethod
        def map_field(field_name: str) -> str:
            if field_name == 'person_id':
                return 'id'
            elif field_name == 'name':
                return 'full_name'
            return field_name

    engine = create_engine('sqlite:///:memory:')
    with engine.connect() as conn:
        conn.execute("""
        CREATE TABLE person (
            id VARCHAR(255) PRIMARY KEY,
            full_name TEXT,
            age INTEGER
        );
        """)

    meta = MetaData()
    return SQLAlchemy(
        PersonCodec,
        meta,
        engine,
        'person',
    )

@pytest.fixture(params=[setup_in_memory_backend, setup_sqlalchemy_backend])
def backend(request):
    return request.param()


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
            person_id=f'person-{i}',
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
            'Expected "{person.person_id}" to have been stored, but it wasn\'t'


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
            person_id=f'person-{i}',
            name=f'name-{i}',
            age=25, # 25 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    for i in range(10, 20):
        test_person = Person(
            person_id=f'person-{i}',
            name=f'name-{i}',
            age=50 # 50 yrs old,
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    # When a subset of records are queried
    queried_persons = person_repository.query(PersonFilter(
        age=50,
    ))

    # Then those records, and only those records, should be returned
    assert len(queried_persons) == 10, \
        f'Expected 10 records to be returned, got {len(queried_persons)}'
    for person in test_persons[10:]:
        assert person in queried_persons, \
            f'Expected "{person.person_id}" to be in results, but it wasn\'t'


def test_query_multiple_filters(backend: BackendProtocol[Person]):
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
            person_id=f'person-{i}',
            name=f'name-{i}',
            age=25, # 25 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    # When a record is queried with multiple filters
    queried_persons = person_repository.query(PersonFilter(
        name='name-0',
        age=25,
    ))

    # Then that record should be returned
    assert len(queried_persons) == 1
    assert queried_persons[0].person_id == 'person-0'


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
            person_id=f'person-{i}',
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
            person_id=f'person-{i}',
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
            person_id=f'person-{i}',
            name=f'name-{i}',
            age=25, # 25 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    for i in range(10, 20):
        test_person = Person(
            person_id=f'person-{i}',
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


def test_update_multiple_filters(backend: BackendProtocol[Person]):
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
            person_id=f'person-{i}',
            name=f'name-{i}',
            age=25, # 25 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    # When one of them is updated via multiple filters
    num_updated = person_repository.update(
        PersonUpdate(
            name='new-name',
        ),
        PersonFilter(
            name='name-0',
            age=25,
        ),
    )

    # Then the count of updated records should be correct
    assert num_updated == 1

    # And the correct record should have been updated
    updated_persons = person_repository.query(PersonFilter(
        name='new-name',
    ))
    assert len(updated_persons) == 1
    assert updated_persons[0].person_id == 'person-0'


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
            person_id=f'person-{i}',
            name=f'name-{i}',
            age=25, # 25 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    for i in range(10, 20):
        test_person = Person(
            person_id=f'person-{i}',
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

def test_delete_multiple_filters(backend: BackendProtocol[Person]):
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
            person_id=f'person-{i}',
            name=f'name-{i}',
            age=25, # 25 yrs old
        )
        person_repository.add([test_person])
        test_persons.append(test_person)

    # When a specific record is deleted with multiple filters
    num_deleted = person_repository.delete(
        PersonFilter(
            name='name-0',
            age=25,
        ),
    )

    # Then that record should be removed
    assert num_deleted == 1
    queried_persons = person_repository.query(PersonFilter(
        name='name-0',
    ))
    assert len(queried_persons) == 0
