"""Setup database with pgvector extension and create tables"""

import asyncio
import sys

# Fix Windows event loop issue
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import text
from app.database import engine, Base
from app.models import UserProfile, JobPosting, JobMatch, ResumeVariant, Application, ScraperJob


async def setup_db():
    """Create pgvector extension and tables"""
    # Create pgvector extension
    async with engine.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            print("✅ pgvector extension enabled")
        except Exception as e:
            print(f"⚠️  pgvector extension: {e}")
        
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(setup_db())
