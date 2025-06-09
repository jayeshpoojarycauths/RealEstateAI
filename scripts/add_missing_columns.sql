-- Add missing columns to scraping_configs table with IF NOT EXISTS checks

-- Add source column if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'scraping_configs' 
        AND column_name = 'source'
    ) THEN
        ALTER TABLE scraping_configs 
        ADD COLUMN source VARCHAR(50);
    END IF;
END $$;

-- Add is_active column if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'scraping_configs' 
        AND column_name = 'is_active'
    ) THEN
        ALTER TABLE scraping_configs 
        ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
    END IF;
END $$;

-- Add schedule column if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'scraping_configs' 
        AND column_name = 'schedule'
    ) THEN
        ALTER TABLE scraping_configs 
        ADD COLUMN schedule VARCHAR(255);
    END IF;
END $$;

-- Add last_run column if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'scraping_configs' 
        AND column_name = 'last_run'
    ) THEN
        ALTER TABLE scraping_configs 
        ADD COLUMN last_run TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- Add next_run column if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'scraping_configs' 
        AND column_name = 'next_run'
    ) THEN
        ALTER TABLE scraping_configs 
        ADD COLUMN next_run TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- Add config column if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'scraping_configs' 
        AND column_name = 'config'
    ) THEN
        ALTER TABLE scraping_configs 
        ADD COLUMN config JSONB;
    END IF;
END $$;

-- Add model_metadata column if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'scraping_configs' 
        AND column_name = 'model_metadata'
    ) THEN
        ALTER TABLE scraping_configs 
        ADD COLUMN model_metadata JSONB;
    END IF;
END $$;

-- Add deleted_at column if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'scraping_configs' 
        AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE scraping_configs 
        ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- Add indexes for better performance
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'scraping_configs' 
        AND indexname = 'idx_scraping_configs_source'
    ) THEN
        CREATE INDEX idx_scraping_configs_source ON scraping_configs(source);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'scraping_configs' 
        AND indexname = 'idx_scraping_configs_is_active'
    ) THEN
        CREATE INDEX idx_scraping_configs_is_active ON scraping_configs(is_active);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'scraping_configs' 
        AND indexname = 'idx_scraping_configs_deleted_at'
    ) THEN
        CREATE INDEX idx_scraping_configs_deleted_at ON scraping_configs(deleted_at);
    END IF;
END $$; 