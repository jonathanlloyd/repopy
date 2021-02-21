"""Helper class for constructng valid repositories"""

from typing import (
    Dict,
    Generic,
    Optional,
    Type,
    get_args,
)

from .backend import BackendProtocol
from .repository import Repository, RepositoryProtocol
from .types import (
    Field,
    FIELD_TYPES,
    EntityType,
    FilterType,
    UpdatesType,
)


class RepositoryFactory(Generic[EntityType, FilterType, UpdatesType]): # pylint: disable=too-few-public-methods
    """Static methods for creating valid repositories"""

    @staticmethod
    def create_repository(
        entity_cls: Type[EntityType],
        filter_cls: Type[FilterType],
        updates_cls: Type[UpdatesType],
        backend: BackendProtocol,
    ) -> RepositoryProtocol[EntityType, FilterType, UpdatesType]:
        """Create a new repository with the provided types and backend"""
        fields: Dict[str, Field] = {}
        for field_name, field_type in entity_cls.__annotations__.items():
            type_args = get_args(field_type)
            is_optional_type = len(type_args) == 2 and type_args[1] == type(None)
            if is_optional_type:
                type_to_check = type_args[0]
            else:
                type_to_check = field_type

            if type_to_check not in FIELD_TYPES:
                raise ValueError(f'Field type "{field_type}" not supported')
            fields[field_name] = field_type

        for field_name, field_type in filter_cls.__annotations__.items():
            if field_name not in fields:
                raise ValueError(
                    f'Filter type not compatible: field "{field_name}"'
                    + ' not in entity type'
                )
            desired_type = fields[field_name]
            if field_type not in (desired_type, Optional[desired_type]):
                raise ValueError(
                    f'Filter type not compatible: field "{field_name}"'
                    + f' should have type {desired_type}/{Optional[desired_type]}'
                )

        for field_name, field_type in updates_cls.__annotations__.items():
            if field_name not in fields:
                raise ValueError(
                    f'Update type not compatible: field "{field_name}"'
                    + ' not in entity type'
                )
            desired_type = fields[field_name]
            if field_type not in (desired_type, Optional[desired_type]):
                raise ValueError(
                    f'Update type not compatible: field "{field_name}"'
                    + f' should have type {desired_type}/{Optional[desired_type]}'
                )

        return Repository(backend, list(fields.keys()))
