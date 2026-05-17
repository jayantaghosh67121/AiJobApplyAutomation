"""Database seed script - populate with sample data"""

import asyncio
import json
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, init_db


async def seed_database():
    """Seed the database with sample data"""
    # Initialize database first
    await init_db()

    async with AsyncSessionLocal() as session:
        print("✓ Database initialized")
        print("✓ Ready for Phase 1: Data models")
        print("\nNext steps:")
        print("1. Define SQLAlchemy models in app/models/")
        print("2. Create Alembic migration: alembic revision --autogenerate")
        print("3. Apply migration: alembic upgrade head")
        print("4. Run this script again to populate sample data")


async def main():
    """Main entry point"""
    try:
        await seed_database()
        print("\n✓ Database seeding complete!")
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
