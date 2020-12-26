import dataclasses
from dataclasses import dataclass
from typing import Optional, Type

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
