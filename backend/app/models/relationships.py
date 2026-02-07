"""
Relationship models for ReBAC (Relationship-Based Access Control)
Stores who has what relationship to which resource
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class ResourceRelationship(BaseModel):
    """
    Stores relationship between user and resource
    Example: user:123 is "owner" of parcel:456
    """
    id: Optional[str] = Field(None, alias="_id")
    user_id: str  # user:123 or ObjectId
    resource_type: str  # "parcel", "establishment", etc.
    resource_id: str  # parcel:456 or ObjectId
    relation_type: str  # "owner", "consultant", "viewer", "collaborator"
    granted_by: Optional[str] = None  # user who granted this relationship
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # optional expiration
    metadata: dict = {}  # additional info (e.g., permissions_level, notes)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class RelationshipManager:
    """Manager for resource relationships in MongoDB"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.relationships
    
    async def add_relationship(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        relation_type: str,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: dict = {}
    ) -> str:
        """Add a new relationship"""
        relationship = {
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "relation_type": relation_type,
            "granted_by": granted_by,
            "granted_at": datetime.utcnow(),
            "expires_at": expires_at,
            "metadata": metadata
        }
        
        # Check if relationship already exists
        existing = await self.collection.find_one({
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "relation_type": relation_type
        })
        
        if existing:
            # Update existing
            await self.collection.update_one(
                {"_id": existing["_id"]},
                {"$set": relationship}
            )
            return str(existing["_id"])
        else:
            # Insert new
            result = await self.collection.insert_one(relationship)
            return str(result.inserted_id)
    
    async def remove_relationship(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        relation_type: Optional[str] = None
    ):
        """Remove a relationship"""
        query = {
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        
        if relation_type:
            query["relation_type"] = relation_type
        
        await self.collection.delete_many(query)
    
    async def get_user_relationships(
        self,
        user_id: str,
        resource_type: Optional[str] = None
    ) -> List[dict]:
        """Get all relationships for a user"""
        query = {"user_id": user_id}
        
        if resource_type:
            query["resource_type"] = resource_type
        
        cursor = self.collection.find(query)
        return await cursor.to_list(length=None)
    
    async def get_resource_relationships(
        self,
        resource_type: str,
        resource_id: str
    ) -> dict:
        """
        Get all relationships for a resource
        Returns: {relation_type: [user_ids]}
        """
        cursor = self.collection.find({
            "resource_type": resource_type,
            "resource_id": resource_id
        })
        
        relationships = await cursor.to_list(length=None)
        
        # Group by relation_type
        result = {}
        for rel in relationships:
            relation_type = rel["relation_type"]
            if relation_type not in result:
                result[relation_type] = []
            result[relation_type].append(rel["user_id"])
        
        return result
    
    async def has_relationship(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        relation_type: Optional[str] = None
    ) -> bool:
        """Check if a relationship exists"""
        query = {
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        
        if relation_type:
            query["relation_type"] = relation_type
        
        count = await self.collection.count_documents(query)
        return count > 0

__all__ = ["ResourceRelationship", "RelationshipManager"]
