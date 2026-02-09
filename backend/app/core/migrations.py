"""
Database Migration System for VitiScan v3
Handles schema changes and data migrations
"""
import asyncio
from datetime import datetime
from typing import Callable, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import db
from app.core.logger import logger

class Migration:
    """Base migration class"""
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.applied_at = None
    
    async def up(self, db: AsyncIOMotorDatabase):
        """Apply migration"""
        raise NotImplementedError("Migration must implement up() method")
    
    async def down(self, db: AsyncIOMotorDatabase):
        """Rollback migration"""
        raise NotImplementedError("Migration must implement down() method")


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.migrations: List[Migration] = []
    
    def register(self, migration: Migration):
        """Register a migration"""
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
    
    async def setup(self):
        """Create migrations collection if not exists"""
        collections = await self.db.list_collection_names()
        if "migrations" not in collections:
            await self.db.create_collection("migrations")
            logger.info("Created migrations collection")
    
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        cursor = self.db.migrations.find({}, {"version": 1})
        return [doc["version"] async for doc in cursor]
    
    async def apply_migration(self, migration: Migration):
        """Apply a single migration"""
        try:
            logger.info(f"Applying migration {migration.version}: {migration.description}")
            await migration.up(self.db)
            
            # Record migration
            await self.db.migrations.insert_one({
                "version": migration.version,
                "description": migration.description,
                "applied_at": datetime.utcnow()
            })
            
            logger.info(f"Migration {migration.version} applied successfully")
            return True
        except Exception as e:
            logger.error(f"Migration {migration.version} failed: {e}")
            return False
    
    async def rollback_migration(self, migration: Migration):
        """Rollback a single migration"""
        try:
            logger.info(f"Rolling back migration {migration.version}: {migration.description}")
            await migration.down(self.db)
            
            # Remove migration record
            await self.db.migrations.delete_one({"version": migration.version})
            
            logger.info(f"Migration {migration.version} rolled back successfully")
            return True
        except Exception as e:
            logger.error(f"Rollback {migration.version} failed: {e}")
            return False
    
    async def migrate(self):
        """Apply all pending migrations"""
        await self.setup()
        applied = await self.get_applied_migrations()
        
        pending = [m for m in self.migrations if m.version not in applied]
        
        if not pending:
            logger.info("No pending migrations")
            return
        
        logger.info(f"Applying {len(pending)} pending migrations")
        
        for migration in pending:
            success = await self.apply_migration(migration)
            if not success:
                logger.error("Migration failed, stopping")
                break
    
    async def rollback(self, steps: int = 1):
        """Rollback last N migrations"""
        applied = await self.get_applied_migrations()
        
        if not applied:
            logger.info("No migrations to rollback")
            return
        
        to_rollback = applied[-steps:]
        migrations_to_rollback = [m for m in self.migrations if m.version in to_rollback]
        migrations_to_rollback.reverse()
        
        for migration in migrations_to_rollback:
            await self.rollback_migration(migration)


# Initialize migration manager
migration_manager = MigrationManager(db)

# Example migrations
class Migration001AddPhoneToUsers(Migration):
    """Add phone_number field to users collection"""
    def __init__(self):
        super().__init__("001", "Add phone_number field to users")
    
    async def up(self, db: AsyncIOMotorDatabase):
        # Add phone_number field to existing users (if not exists)
        await db.users.update_many(
            {"phone_number": {"$exists": False}},
            {"$set": {"phone_number": None}}
        )
    
    async def down(self, db: AsyncIOMotorDatabase):
        # Remove phone_number field
        await db.users.update_many(
            {},
            {"$unset": {"phone_number": ""}}
        )

class Migration002AddCoordinatesParcels(Migration):
    """Add coordinates field to parcels collection"""
    def __init__(self):
        super().__init__("002", "Add coordinates (GeoJSON) to parcels")
    
    async def up(self, db: AsyncIOMotorDatabase):
        # Add coordinates field (default empty array)
        await db.parcels.update_many(
            {"coordinates": {"$exists": False}},
            {"$set": {"coordinates": []}}
        )
        # Create geospatial index
        await db.parcels.create_index([("coordinates", "2dsphere")])
    
    async def down(self, db: AsyncIOMotorDatabase):
        # Remove coordinates field
        await db.parcels.update_many(
            {},
            {"$unset": {"coordinates": ""}}
        )
        # Drop geospatial index
        await db.parcels.drop_index("coordinates_2dsphere")

class Migration003BetaRequests(Migration):
    """Create beta_requests collection with indexes"""
    def __init__(self):
        super().__init__("003", "Create beta_requests collection")
    
    async def up(self, db: AsyncIOMotorDatabase):
        # Create collection
        collections = await db.list_collection_names()
        if "beta_requests" not in collections:
            await db.create_collection("beta_requests")
        
        # Create indexes
        await db.beta_requests.create_index("email", unique=True)
        await db.beta_requests.create_index("status")
        await db.beta_requests.create_index("created_at")
    
    async def down(self, db: AsyncIOMotorDatabase):
        # Drop collection
        await db.drop_collection("beta_requests")

class Migration004Relationships(Migration):
    """Create relationships collection for ReBAC authorization"""
    def __init__(self):
        super().__init__("004", "Create relationships collection for ReBAC")
    
    async def up(self, db: AsyncIOMotorDatabase):
        # Create collection
        collections = await db.list_collection_names()
        if "relationships" not in collections:
            await db.create_collection("relationships")
        
        # Create compound indexes for efficient queries
        await db.relationships.create_index([
            ("user_id", 1),
            ("resource_type", 1),
            ("resource_id", 1)
        ])
        await db.relationships.create_index([
            ("resource_type", 1),
            ("resource_id", 1)
        ])
        await db.relationships.create_index("relation_type")
        await db.relationships.create_index("granted_at")
        
        # Add initial owner relationships for existing resources
        # Parcels
        parcels = await db.parcels.find({}).to_list(length=None)
        for parcel in parcels:
            await db.relationships.insert_one({
                "user_id": f"user:{parcel['user_id']}",
                "resource_type": "parcel",
                "resource_id": f"parcel:{parcel['_id']}",
                "relation_type": "owner",
                "granted_by": "system_migration",
                "granted_at": parcel.get("created_at"),
                "metadata": {"migrated": True}
            })
        
        # Establishments
        establishments = await db.establishments.find({}).to_list(length=None)
        for est in establishments:
            await db.relationships.insert_one({
                "user_id": f"user:{est['user_id']}",
                "resource_type": "establishment",
                "resource_id": f"establishment:{est['_id']}",
                "relation_type": "owner",
                "granted_by": "system_migration",
                "granted_at": est.get("created_at"),
                "metadata": {"migrated": True}
            })
    
    async def down(self, db: AsyncIOMotorDatabase):
        # Drop collection
        await db.drop_collection("relationships")

class Migration005AuditLogsAndTokens(Migration):
    """Create audit_logs and capability_tokens collections"""
    def __init__(self):
        super().__init__("005", "Create audit_logs and capability_tokens for enterprise features")
    
    async def up(self, db: AsyncIOMotorDatabase):
        # Create audit_logs collection
        collections = await db.list_collection_names()
        if "audit_logs" not in collections:
            await db.create_collection("audit_logs")
        
        # Indexes for audit_logs
        await db.audit_logs.create_index("timestamp")
        await db.audit_logs.create_index("user_id")
        await db.audit_logs.create_index("action")
        await db.audit_logs.create_index("outcome")
        await db.audit_logs.create_index([
            ("user_id", 1),
            ("timestamp", -1)
        ])
        
        # Create capability_tokens collection
        if "capability_tokens" not in collections:
            await db.create_collection("capability_tokens")
        
        # Indexes for capability_tokens
        await db.capability_tokens.create_index("token", unique=True)
        await db.capability_tokens.create_index("issuer_id")
        await db.capability_tokens.create_index("expires_at")
        await db.capability_tokens.create_index([
            ("resource_type", 1),
            ("resource_id", 1)
        ])
    
    async def down(self, db: AsyncIOMotorDatabase):
        # Drop collections
        await db.drop_collection("audit_logs")
        await db.drop_collection("capability_tokens")


class Migration006UsernameIndex(Migration):
    """Create case-insensitive unique index on users.username and add company_name field"""
    def __init__(self):
        super().__init__("006", "Add company_name field and case-insensitive unique index on username")
    
    async def up(self, db: AsyncIOMotorDatabase):
        # Ensure company_name exists on user docs
        await db.users.update_many(
            {"company_name": {"$exists": False}},
            {"$set": {"company_name": None}}
        )
        # Create case-insensitive unique index on username (collation strength 2)
        try:
            from pymongo.collation import Collation
            await db.users.create_index(
                [("username", 1)],
                name="username_unique_ci",
                unique=True,
                collation=Collation(locale="en", strength=2)
            )
        except Exception as e:
            # Log and continue; some Mongo setups may not support collation in tests
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not create CI username index: {e}")
    
    async def down(self, db: AsyncIOMotorDatabase):
        # Remove company_name field and drop index
        try:
            await db.users.drop_index("username_unique_ci")
        except Exception:
            pass
        await db.users.update_many({}, {"$unset": {"company_name": ""}})

# Register migrations
migration_manager.register(Migration001AddPhoneToUsers())
migration_manager.register(Migration002AddCoordinatesParcels())
migration_manager.register(Migration003BetaRequests())
migration_manager.register(Migration004Relationships())
migration_manager.register(Migration005AuditLogsAndTokens())
migration_manager.register(Migration006UsernameIndex())

# Export
__all__ = ["migration_manager", "Migration", "MigrationManager"]
