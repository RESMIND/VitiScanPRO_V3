"""
CLI tool for running database migrations
Usage:
    python migrate.py up           # Apply all pending migrations
    python migrate.py down         # Rollback last migration
    python migrate.py down 3       # Rollback last 3 migrations
    python migrate.py status       # Show migration status
"""
import asyncio
import sys
from app.core.migrations import migration_manager
from app.core.logger import logger

async def show_status():
    """Show current migration status"""
    await migration_manager.setup()
    applied = await migration_manager.get_applied_migrations()
    
    print("\n" + "="*60)
    print("Migration Status")
    print("="*60 + "\n")
    
    print(f"Total migrations: {len(migration_manager.migrations)}")
    print(f"Applied: {len(applied)}")
    print(f"Pending: {len(migration_manager.migrations) - len(applied)}\n")
    
    print("Migrations:")
    for migration in migration_manager.migrations:
        status = "✓ Applied" if migration.version in applied else "○ Pending"
        print(f"  {status} - {migration.version}: {migration.description}")
    print()

async def migrate_up():
    """Apply all pending migrations"""
    await migration_manager.migrate()

async def migrate_down(steps: int = 1):
    """Rollback migrations"""
    await migration_manager.rollback(steps)

async def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [up|down|status] [steps]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "status":
            await show_status()
        elif command == "up":
            await migrate_up()
            await show_status()
        elif command == "down":
            steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            await migrate_down(steps)
            await show_status()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Migration command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
