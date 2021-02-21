from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import dataclasses

from repopy import (
    RepositoryFactory,
    RepositoryMiddleware,
    AddMethodType,
    QueryMethodType,
    UpdateMethodType,
    DeleteMethodType,
)
from repopy.backends import InMemory


@dataclass
class Person:
    person_id: str
    name: str
    age: int
    soft_deleted_at: Optional[datetime] = None


@dataclass
class PersonFilter:
    name: Optional[str] = None
    age: Optional[int] = None


@dataclass
class PersonUpdate:
    name: Optional[str] = None


def copy_func(person: Person) -> Person:
    return Person(**dataclasses.asdict(person))


def test_add() -> None:
    # Given a middleware with an add method
    middleware_was_called = False

    class AddMiddleware(RepositoryMiddleware):
        def add(
            self,
            entities: List[Person],
            next_func: AddMethodType[Person],
        ):
            nonlocal middleware_was_called
            middleware_was_called = True
            return next_func(entities)

    # And a repository with that middleware applied
    backend: InMemory[Person] = InMemory(copy_func)
    repository = RepositoryFactory.create_repository(
        Person,
        PersonFilter,
        PersonUpdate,
        backend,
    ).with_middleware(AddMiddleware())

    # When add is called
    repository.add([Person(
        person_id='1',
        name='Alice',
        age=28,
    )])

    # Then the middleware should have been called
    assert middleware_was_called


def test_query() -> None:
    # Given a middleware with a query method
    middleware_was_called = False

    class QueryMiddleware(RepositoryMiddleware):
        def query(
            self,
            filters: PersonFilter,
            next_func: QueryMethodType[PersonFilter, Person],
            limit: int = None,
        ) -> List[Person]:
            nonlocal middleware_was_called
            middleware_was_called = True
            return next_func(filters, limit)

    # And a repository with that middleware applied
    backend: InMemory[Person] = InMemory(copy_func)
    repository = RepositoryFactory.create_repository(
        Person,
        PersonFilter,
        PersonUpdate,
        backend,
    ).with_middleware(QueryMiddleware())

    # When query is called
    repository.query(PersonFilter(
        name='Alice',
    ))

    # Then the middleware should have been called
    assert middleware_was_called


def test_update() -> None:
    # Given a middleware with an update method
    middleware_was_called = False

    class QueryMiddleware(RepositoryMiddleware):
        def update(
            self,
            updates: PersonUpdate,
            filters: PersonFilter,
            next_func: UpdateMethodType[PersonUpdate, PersonFilter],
        ) -> int:
            nonlocal middleware_was_called
            middleware_was_called = True
            return next_func(updates, filters)

    # And a repository with that middleware applied
    backend: InMemory[Person] = InMemory(copy_func)
    repository = RepositoryFactory.create_repository(
        Person,
        PersonFilter,
        PersonUpdate,
        backend,
    ).with_middleware(QueryMiddleware())

    # When update is called
    repository.update(
        PersonUpdate(name='Alice'),
        PersonFilter(),
    )

    # Then the middleware should have been called
    assert middleware_was_called


def test_delete() -> None:
    # Given a middleware with a delete method
    middleware_was_called = False

    class DeleteMiddleware(RepositoryMiddleware):
        def delete(
            self,
            filters: PersonFilter,
            next_func: DeleteMethodType[PersonFilter],
        ) -> int:
            nonlocal middleware_was_called
            middleware_was_called = True
            return next_func(filters)

    # And a repository with that middleware applied
    backend: InMemory[Person] = InMemory(copy_func)
    repository = RepositoryFactory.create_repository(
        Person,
        PersonFilter,
        PersonUpdate,
        backend,
    ).with_middleware(DeleteMiddleware())

    # When update is called
    repository.delete(PersonFilter())

    # Then the middleware should have been called
    assert middleware_was_called
