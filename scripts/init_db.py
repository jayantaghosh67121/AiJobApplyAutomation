"""Initialize database tables using SQLAlchemy directly"""

import asyncio
import selectors
import sys

# Fix Windows event loop issue
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.database import engine, Base
from app.models import UserProfile, JobPosting, JobMatch, ResumeVariant, Application, ScraperJob


async def init_db():
    """Create all tables in the database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
