"""Base scraper class and job scraper implementations"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import JobPosting, ScraperJob
from app.services.ai_matching import extract_job_keywords

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for job scrapers"""
    
    source_name: str
    description: str
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.jobs_scraped = 0
        self.jobs_added = 0
        self.jobs_updated = 0
        self.errors: List[str] = []
    
    @abstractmethod
    async def scrape(self) -> List[dict]:
        """
        Scrape jobs from source.
        
        Returns list of job dicts with keys:
        - title
        - company
        - description
        - location
        - salary_min (optional)
        - salary_max (optional)
        - job_type (optional)
        - posted_date (optional)
        - source_url
        - external_id (unique per source)
        """
        pass
    
    async def save_jobs(self, jobs: List[dict]) -> tuple[int, int]:
        """Save scraped jobs to database. Returns (added, updated) counts"""
        added = 0
        updated = 0
        
        for job_data in jobs:
            try:
                external_id = f"{self.source_name}_{job_data['external_id']}"
                
                # Check if job already exists
                result = await self.db.execute(
                    select(JobPosting).where(JobPosting.external_id == external_id)
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    # Update existing job
                    existing.title = job_data['title']
                    existing.company = job_data['company']
                    existing.description = job_data['description']
                    existing.location = job_data.get('location')
                    existing.salary_min = job_data.get('salary_min')
                    existing.salary_max = job_data.get('salary_max')
                    existing.job_type = job_data.get('job_type')
                    existing.posted_date = job_data.get('posted_date')
                    existing.source_url = job_data['source_url']
                    existing.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    # Create new job
                    new_job = JobPosting(
                        external_id=external_id,
                        title=job_data['title'],
                        company=job_data['company'],
                        description=job_data['description'],
                        location=job_data.get('location'),
                        salary_min=job_data.get('salary_min'),
                        salary_max=job_data.get('salary_max'),
                        job_type=job_data.get('job_type'),
                        posted_date=job_data.get('posted_date'),
                        source=self.source_name,
                        source_url=job_data['source_url'],
                        scraped_at=datetime.utcnow()
                    )
                    self.db.add(new_job)
                    added += 1
            
            except Exception as e:
                error_msg = f"Error saving job {job_data.get('title', 'Unknown')}: {str(e)}"
                logger.error(error_msg)
                self.errors.append(error_msg)
        
        await self.db.commit()
        return added, updated
    
    async def run(self) -> dict:
        """Run the full scraper pipeline"""
        scraper_job = ScraperJob(
            source=self.source_name,
            status="RUNNING",
            started_at=datetime.utcnow()
        )
        self.db.add(scraper_job)
        await self.db.commit()
        
        try:
            # Scrape jobs
            jobs = await self.scrape()
            self.jobs_scraped = len(jobs)
            logger.info(f"{self.source_name}: Scraped {self.jobs_scraped} jobs")
            
            # Save to database
            added, updated = await self.save_jobs(jobs)
            self.jobs_added = added
            self.jobs_updated = updated
            logger.info(f"{self.source_name}: Added {added}, Updated {updated}")
            
            # Mark as completed
            scraper_job.status = "COMPLETED"
            scraper_job.jobs_scraped = self.jobs_scraped
            scraper_job.jobs_added = added
            scraper_job.jobs_updated = updated
            scraper_job.completed_at = datetime.utcnow()
            
            duration = (scraper_job.completed_at - scraper_job.started_at).total_seconds()
            scraper_job.duration_seconds = int(duration)
            
        except Exception as e:
            error_msg = f"Scraper failed: {str(e)}"
            logger.error(error_msg)
            scraper_job.status = "FAILED"
            scraper_job.error_message = error_msg
            scraper_job.errors = self.errors
            scraper_job.completed_at = datetime.utcnow()
        
        await self.db.commit()
        
        return {
            "source": self.source_name,
            "status": scraper_job.status,
            "scraped": self.jobs_scraped,
            "added": self.jobs_added,
            "updated": self.jobs_updated,
            "errors": self.errors
        }


class LinkedInScraper(BaseScraper):
    """LinkedIn job scraper (requires authentication/API)"""
    
    source_name = "linkedin"
    description = "LinkedIn job listings"
    
    async def scrape(self) -> List[dict]:
        """Placeholder - LinkedIn requires special handling"""
        # This would use the LinkedIn API or Playwright for scraping
        logger.info("LinkedIn scraper not yet implemented")
        return []


class IndeedScraper(BaseScraper):
    """Indeed job scraper"""
    
    source_name = "indeed"
    description = "Indeed job listings"
    
    async def scrape(self) -> List[dict]:
        """Placeholder - Indeed scraper implementation"""
        # This would use Playwright or BeautifulSoup for scraping
        logger.info("Indeed scraper not yet implemented")
        return []


class GeneralJobScraper(BaseScraper):
    """Generic job scraper for static job sources"""
    
    source_name = "general"
    description = "Generic job listings"
    
    async def scrape(self) -> List[dict]:
        """Placeholder for generic scraper"""
        logger.info("General scraper not yet implemented")
        return []
