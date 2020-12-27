"""In-memory generic implementation of the repository protocol"""
# pylint: disable=missing-function-docstring

from typing import (
    Any,
    Dict,
    Generic,
    List,
    Mapping,
    Optional,
    Protocol,
    Type,
)

from sqlalchemy import Table # type: ignore

from ..repository import (
    EntityType,
    Field,
)


class DictCodec(Protocol, Generic[EntityType]):
    """Static methods for converting desired type to/from a dict keyed by
    the desired column name in the relevant table"""
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> EntityType:
        pass

    @staticmethod
    def to_dict(entity: EntityType) -> Dict[str, Any]:
        pass


class SQLAlchemy(Generic[EntityType]):
    """SQLAlchemy based backend for RDBMS support"""
    _codec: Type[DictCodec[EntityType]]
    _engine: Any
    _table: Any

    def __init__(
            self,
            codec: Type[DictCodec[EntityType]],
            meta: Any,
            engine: Any,
            table_name: str,
        ):
        self._codec = codec
        self._engine = engine
        self._table = Table(
            table_name,
            meta,
            autoload=True,
            autoload_with=engine,
        )

    def add(self, entities: List[EntityType]):
        conn = self._engine.connect()
        conn.execute(self._table.insert(None), [
            self._codec.to_dict(entity)
            for entity in entities
        ])

    def query(
        self,
        filters: Mapping[str, Field],
        limit: Optional[int],
    ) -> List[EntityType]:
        conn = self._engine.connect()

        select = self._table.select()
        if filters:
            select = select.where(*[
                getattr(self._table.c, filter_name) == filter_value
                for filter_name, filter_value in filters.items()
            ])
        if limit is not None:
            select = select.limit(limit)

        results = conn.execute(select)
        return [
            self._codec.from_dict(dict(row.items()))
            for row in results
        ]

    def update(
        self,
        updates: Mapping[str, Field],
        filters: Mapping[str, Field],
    ) -> int:
        if not updates:
            return 0

        conn = self._engine.connect()
        update = self._table.update(None).values({
            getattr(self._table.c, field_name): new_value
            for field_name, new_value in updates.items()
        })
        if filters:
            update = update.where(*[
                getattr(self._table.c, filter_name) == filter_value
                for filter_name, filter_value in filters.items()
            ])

        results = conn.execute(update)
        return results.rowcount

    def delete(self, filters: Mapping[str, Field]) -> int:
        conn = self._engine.connect()
        delete = self._table.delete(None)
        if filters:
            delete = delete.where(*[
                getattr(self._table.c, filter_name) == filter_value
                for filter_name, filter_value in filters.items()
            ])
        results = conn.execute(delete)
        return results.rowcount

def _row2dict(row):
    data = {}
    for column in row.__table__.columns:
        data[column.name] = str(getattr(row, column.name))
    return data
