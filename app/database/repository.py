"""
Repository pattern implementation.
Provides abstract base and concrete implementations for data access.
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository.
    
    Defines the contract for all repository implementations.
    All database access must go through repositories, never
    directly from routes or services.
    
    Type parameter T represents the model class.
    """
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity instance if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 10) -> List[T]:
        """Get all entities with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of entity instances
        """
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity.
        
        Args:
            entity: Entity to create
            
        Returns:
            Created entity with ID
        """
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an existing entity.
        
        Args:
            entity: Entity with updated values
            
        Returns:
            Updated entity
        """
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete an entity by ID.
        
        Args:
            id: Entity ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Count total entities.
        
        Returns:
            Number of entities
        """
        pass
