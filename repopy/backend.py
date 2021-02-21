"""Public interface for backends that support repository queries"""

from typing import (
    Generic,
    List,
    Mapping,
    Optional,
    Protocol,
)

from .types import (
    Field,
    EntityType,
)


class BackendProtocol(Protocol, Generic[EntityType]):
    """Interface that must be implemented by storage backends for Repopy
    repositories"""

    def add(self, entities: List[EntityType]):
        """Store one or more new records via this backend"""

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
