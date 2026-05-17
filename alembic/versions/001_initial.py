"""Create initial models

Revision ID: 001_initial
Revises: 
Create Date: 2026-05-17 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


def upgrade() -> None:
    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('resume_text', sa.Text(), nullable=True),
        sa.Column('resume_embedding', Vector(384), nullable=True),
        sa.Column('resume_file_name', sa.String(255), nullable=True),
        sa.Column('resume_uploaded_at', sa.DateTime(), nullable=True),
        sa.Column('target_roles', sa.JSON(), nullable=True),
        sa.Column('target_companies', sa.JSON(), nullable=True),
        sa.Column('blacklist_companies', sa.JSON(), nullable=True),
        sa.Column('min_salary', sa.Integer(), nullable=True),
        sa.Column('preferred_locations', sa.JSON(), nullable=True),
        sa.Column('auto_apply_threshold', sa.Float(), nullable=False, server_default='0.75'),
        sa.Column('generate_cover_letters', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('use_custom_resume', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'])

    # Create job_postings table
    op.create_table(
        'job_postings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(255), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('description_embedding', Vector(384), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('currency', sa.String(10), nullable=False, server_default='USD'),
        sa.Column('job_type', sa.String(50), nullable=True),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('source_url', sa.String(1024), nullable=False),
        sa.Column('posted_date', sa.DateTime(), nullable=True),
        sa.Column('scraped_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_id'),
    )
    op.create_index('ix_job_postings_title', 'job_postings', ['title'])
    op.create_index('ix_job_postings_company', 'job_postings', ['company'])
    op.create_index('ix_job_postings_source', 'job_postings', ['source'])

    # Create resume_variants table
    op.create_table(
        'resume_variants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(384), nullable=True),
        sa.Column('is_template', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('format_type', sa.String(50), nullable=False, server_default='markdown'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id']),
        sa.ForeignKeyConstraint(['job_id'], ['job_postings.id']),
    )
    op.create_index('ix_resume_variants_user_id', 'resume_variants', ['user_id'])

    # Create job_matches table
    op.create_table(
        'job_matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('match_score', sa.Float(), nullable=False),
        sa.Column('match_reasons', sa.JSON(), nullable=True),
        sa.Column('required_skills_match', sa.Float(), nullable=True),
        sa.Column('preferred_skills_match', sa.Float(), nullable=True),
        sa.Column('salary_match', sa.Float(), nullable=True),
        sa.Column('location_match', sa.Float(), nullable=True),
        sa.Column('cover_letter', sa.Text(), nullable=True),
        sa.Column('tailored_resume_id', sa.Integer(), nullable=True),
        sa.Column('user_status', sa.String(50), nullable=False, server_default='NEW'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id']),
        sa.ForeignKeyConstraint(['job_id'], ['job_postings.id']),
        sa.ForeignKeyConstraint(['tailored_resume_id'], ['resume_variants.id']),
    )
    op.create_index('ix_job_matches_user_id', 'job_matches', ['user_id'])

    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='SUBMITTED'),
        sa.Column('application_method', sa.String(50), nullable=False),
        sa.Column('resume_variant_id', sa.Integer(), nullable=True),
        sa.Column('cover_letter_used', sa.Text(), nullable=True),
        sa.Column('auto_applied', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('application_url', sa.String(1024), nullable=True),
        sa.Column('confirmation_email', sa.String(1024), nullable=True),
        sa.Column('tracking_number', sa.String(255), nullable=True),
        sa.Column('recruiter_name', sa.String(255), nullable=True),
        sa.Column('recruiter_email', sa.String(255), nullable=True),
        sa.Column('last_message_date', sa.DateTime(), nullable=True),
        sa.Column('last_message_subject', sa.String(255), nullable=True),
        sa.Column('applied_date', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user_profiles.id']),
        sa.ForeignKeyConstraint(['job_id'], ['job_postings.id']),
        sa.ForeignKeyConstraint(['resume_variant_id'], ['resume_variants.id']),
    )
    op.create_index('ix_applications_user_id', 'applications', ['user_id'])

    # Create scraper_jobs table
    op.create_table(
        'scraper_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='PENDING'),
        sa.Column('jobs_scraped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_added', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_updated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('errors', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('next_scheduled', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scraper_jobs_source', 'scraper_jobs', ['source'])


def downgrade() -> None:
    op.drop_index('ix_scraper_jobs_source', table_name='scraper_jobs')
    op.drop_table('scraper_jobs')
    op.drop_index('ix_applications_user_id', table_name='applications')
    op.drop_table('applications')
    op.drop_index('ix_job_matches_user_id', table_name='job_matches')
    op.drop_table('job_matches')
    op.drop_index('ix_resume_variants_user_id', table_name='resume_variants')
    op.drop_table('resume_variants')
    op.drop_index('ix_job_postings_source', table_name='job_postings')
    op.drop_index('ix_job_postings_company', table_name='job_postings')
    op.drop_index('ix_job_postings_title', table_name='job_postings')
    op.drop_table('job_postings')
    op.drop_index('ix_user_profiles_user_id', table_name='user_profiles')
    op.drop_table('user_profiles')
