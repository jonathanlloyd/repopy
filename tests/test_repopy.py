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


def setup_in_memory_backend():
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

    # And a test record
    test_person = Person(
        id='person-1',
        name='Alice',
        age=32,
    )

    # When add is called
    person_repository.add(test_person)

    # Then the record should be returned when queried
    persons = person_repository.query(PersonFilter(
        name='Alice',
    ))

    assert len(persons) == 1, \
        "Expected a single record to be returned"
    assert persons[0] == test_person, \
        "Expected inserted record to be returned unaltered"


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
        person_repository.add(test_person)
        test_persons.append(test_person)

    for i in range(10, 20):
        test_person = Person(
            id=f'person-{i}',
            name=f'name-{i}',
            age=50 # 50 yrs old,
        )
        person_repository.add(test_person)
        test_persons.append(test_person)

    # When a subset of records are queried
    query_set = [p.id for p in test_persons[:5]]
    queried_persons = person_repository.query(PersonFilter(
        age=50,
    ))

    # Then those records, and only those records, should be returned
    assert len(queried_persons) == 10
    for person in test_persons[10:]:
        assert person in queried_persons
