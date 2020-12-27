[![Build Status](https://github.com/jonathanlloyd/repopy/workflows/ci/badge.svg)](https://github.com/jonathanlloyd/repopy/actions)

# repopy

Interface (and default implementation set) for the Repository Pattern in Python

## Features

- Pure domain models - use normal Python dataclasses (or other annotated domain
  models) without any special annotations for the underlying database.
- Type safe - All queries have mypy-compatible typed signatures.
- Pluggable backend support - Use one of the included backends or provide your
  own for compatibility with any database/persistence layer.
- Built-in test double - Use the built-in `InMemory` backend to test your
  business logic that depends on persistence.

## Setup

### Create Types
First, create the types you would like to use for querying the repository
(dataclasses recommended):

```Python
# Entity type - the domain model you'd like to store in the repository
@dataclass
class Person:
  first_name: str
  second_name: str
  age: int

# Filter type - the subset of fields you'd like to use for querying/partial
# updates and deletes
@dataclass
class PersonFilter:
  # Optional, so that we don't have to provide all fields when querying
  first_name: Optional[str]
  second_name: Optional[str]

# Update type - the subset of fields you'd like to be able to mutate with
# the update method
@dataclass
class PersonFilter:
  # Optional, so that we don't have to provide all fields when querying
  age: Optional[int]
```


### Set up backend
Next, you will need to create a backend to store the repository records.
In this example, we will use the built-in in-memory backend:
```Python
import dataclasses

from repopy.backends import InMemory

def copy_dataclass(dc):
  return type(dc)(**dataclasses.asdict(dc))

backend = InMemory(copy_func=copy_dataclass)
```


### Create a repository
```Python
from repopy import RepositoryFactory

person_repository = RepositoryFactory.create_repository(
  Person,
  PersonFilter,
  PersonUpdate,
  backend,
)
```

## API
<table>
  <tr>
    <th>method</th>
    <th>args</th>
    <th>returns</th>
  </tr>
  <tr>
    <td>add</td>
    <td>
      <ul>
        <li>entity: EntityType</li>
      </ul>
    </td>
    <td>None</td>
  </tr>
  <tr>
    <td>query</td>
    <td>
      <ul>
        <li>filters: FilterType</li>
      </ul>
    </td>
    <td>results: List[EntityType]</td>
  </tr>
  <tr>
    <td>update</td>
    <td>
      <ul>
        <li>updates: UpdateType</li>
      </ul>
      <ul>
        <li>filters: FilterType</li>
      </ul>
    </td>
    <td>num_updated: int</td>
  </tr>
  <tr>
    <td>delete</td>
    <td>
      <ul>
        <li>filters: FilterType</li>
      </ul>
    </td>
    <td>num_deleted: int</td>
  </tr>
</table>
