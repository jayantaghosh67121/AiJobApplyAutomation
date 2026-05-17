-- Initialize database extensions and basic setup
-- This script is run automatically by docker-compose on first startup

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for the application
CREATE SCHEMA IF NOT EXISTS job_bot;

-- Log initialization
SELECT 'Database initialized successfully' AS status;
