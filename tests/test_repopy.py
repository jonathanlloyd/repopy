from dataclasses import dataclass
from typing import Optional, Type

import pytest # type: ignore

from repopy import Repository
from repopy.implementations import InMemory


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


@pytest.fixture(params=[InMemory])
def person_repository(request) -> Repository[Person, PersonFilter, PersonUpdate]:
    return request.param()


def test_add(person_repository: Repository[Person, PersonFilter, PersonUpdate]):
    test_person = Person(
        id='person-1',
        name='Alice',
        age=32,
    )

    person_repository.add(test_person)

    persons = person_repository.query(PersonFilter(
        name='Alice',
    ))

    assert len(persons) == 1, \
        "Expected a single record to be returned"
    assert persons[0] == test_person, \
        "Expected inserted record to be returned unaltered"
