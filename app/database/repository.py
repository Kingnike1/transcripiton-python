"""
Repository pattern implementation.
Provides abstract contracts for data access.
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository.

    Repositories encapsulate database access and stage persistence changes.
    They never own transaction boundaries; commits and rollbacks belong to the
    service layer through the unit of work.

    Type parameter T represents the model class.
    """

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 10) -> List[T]:
        """Get all entities with pagination."""
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        """Stage a new entity and flush it without committing."""
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """Stage entity changes and flush them without committing."""
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Stage an entity deletion without committing."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total entities."""
        pass
