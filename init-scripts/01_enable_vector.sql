-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;
-- Create schema for embeddings
CREATE SCHEMA IF NOT EXISTS embeddings;
-- Set search path to include embeddings schema
ALTER DATABASE semantic_search_db set search_path TO embeddings, public;