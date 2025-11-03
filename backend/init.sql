-- Initialize the compression database
CREATE DATABASE compression_db;

-- Create the postgres user if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres') THEN
        CREATE ROLE postgres WITH LOGIN SUPERUSER CREATEDB CREATEROLE PASSWORD 'password';
    END IF;
END
$$;

-- Grant all privileges to postgres user
GRANT ALL PRIVILEGES ON DATABASE compression_db TO postgres;

-- Connect to the compression_db and create tables
\c compression_db;

-- Create tables for the compression application
CREATE TABLE IF NOT EXISTS compression_results (
    id SERIAL PRIMARY KEY,
    content_hash VARCHAR(64) NOT NULL,
    original_size INTEGER NOT NULL,
    compressed_size INTEGER NOT NULL,
    algorithm VARCHAR(50) NOT NULL,
    compression_ratio DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS algorithm_performance (
    id SERIAL PRIMARY KEY,
    algorithm VARCHAR(50) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    avg_compression_ratio DECIMAL(5,2) NOT NULL,
    avg_processing_time DECIMAL(10,3) NOT NULL,
    sample_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,3) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_compression_results_hash ON compression_results(content_hash);
CREATE INDEX IF NOT EXISTS idx_compression_results_algorithm ON compression_results(algorithm);
CREATE INDEX IF NOT EXISTS idx_algorithm_performance_algorithm ON algorithm_performance(algorithm);
CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);