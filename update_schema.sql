-- Update: Remove user_id from communication_preferences if it exists
ALTER TABLE communication_preferences DROP COLUMN IF EXISTS user_id;

-- Update: Create user_communication_preferences join table with unique constraint
CREATE TABLE user_communication_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    communication_preferences_id UUID NOT NULL REFERENCES communication_preferences(id),
    channel VARCHAR NOT NULL,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, communication_preferences_id, channel)
);

ALTER TABLE customers ADD COLUMN domain VARCHAR(255);

ALTER TABLE leads ADD COLUMN source VARCHAR(255);
ALTER TABLE leads ADD COLUMN status VARCHAR(50) DEFAULT 'new';
ALTER TABLE leads ADD COLUMN notes TEXT;
ALTER TABLE leads ADD COLUMN assigned_to UUID REFERENCES users(id);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS first_name VARCHAR(255);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_name VARCHAR(255);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS created_by UUID;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS updated_by UUID;
-- Add other columns as needed 

-- Convert leads.customer_id from INTEGER to UUID
-- 1. Drop existing foreign key constraint if any
ALTER TABLE leads DROP CONSTRAINT IF EXISTS leads_customer_id_fkey;

-- 2. Alter the column type from INTEGER to UUID
ALTER TABLE leads ALTER COLUMN customer_id TYPE UUID USING customer_id::uuid;

-- 3. Re-add the foreign key constraint (if customers.id is UUID)
ALTER TABLE leads ADD CONSTRAINT leads_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customers(id); 

-- Convert customer_id columns to UUID in all relevant tables

-- communication_preferences
ALTER TABLE communication_preferences DROP CONSTRAINT IF EXISTS communication_preferences_customer_id_fkey;
ALTER TABLE communication_preferences ALTER COLUMN customer_id TYPE UUID USING customer_id::uuid;
ALTER TABLE communication_preferences ADD CONSTRAINT communication_preferences_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customers(id);

-- projects
ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_customer_id_fkey;
ALTER TABLE projects ALTER COLUMN customer_id TYPE UUID USING customer_id::uuid;
ALTER TABLE projects ADD CONSTRAINT projects_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customers(id);

-- outreach_logs
ALTER TABLE outreach_logs DROP CONSTRAINT IF EXISTS outreach_logs_customer_id_fkey;
ALTER TABLE outreach_logs ALTER COLUMN customer_id TYPE UUID USING customer_id::uuid;
ALTER TABLE outreach_logs ADD CONSTRAINT outreach_logs_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customers(id);

-- real_estate_projects
ALTER TABLE real_estate_projects DROP CONSTRAINT IF EXISTS real_estate_projects_customer_id_fkey;
ALTER TABLE real_estate_projects ALTER COLUMN customer_id TYPE UUID USING customer_id::uuid;
ALTER TABLE real_estate_projects ADD CONSTRAINT real_estate_projects_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customers(id);

-- real_estate_buyers
ALTER TABLE real_estate_buyers DROP CONSTRAINT IF EXISTS real_estate_buyers_customer_id_fkey;
ALTER TABLE real_estate_buyers ALTER COLUMN customer_id TYPE UUID USING customer_id::uuid;
ALTER TABLE real_estate_buyers ADD CONSTRAINT real_estate_buyers_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customers(id);

-- interaction_logs
ALTER TABLE interaction_logs DROP CONSTRAINT IF EXISTS interaction_logs_customer_id_fkey;
ALTER TABLE interaction_logs ALTER COLUMN customer_id TYPE UUID USING customer_id::uuid;
ALTER TABLE interaction_logs ADD CONSTRAINT interaction_logs_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customers(id);

-- scraping_configs
ALTER TABLE scraping_configs DROP CONSTRAINT IF EXISTS scraping_configs_customer_id_fkey;
ALTER TABLE scraping_configs ALTER COLUMN customer_id TYPE UUID USING customer_id::uuid;
ALTER TABLE scraping_configs ADD CONSTRAINT scraping_configs_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customers(id);

-- Add customer_id column to audit_logs if it does not exist
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS customer_id UUID;
ALTER TABLE audit_logs ADD CONSTRAINT IF NOT EXISTS audit_logs_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES customers(id);

-- Convert assigned_to column to UUID if it exists
ALTER TABLE leads DROP CONSTRAINT IF EXISTS leads_assigned_to_fkey;
ALTER TABLE leads ALTER COLUMN assigned_to TYPE UUID USING assigned_to::uuid;
ALTER TABLE leads ADD CONSTRAINT leads_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL;

-- Add columns
ALTER TABLE users
ADD COLUMN first_name VARCHAR(100),
ADD COLUMN last_name VARCHAR(100),
ADD COLUMN last_login TIMESTAMP,
ADD COLUMN model_metadata JSON,
ADD COLUMN reset_token VARCHAR(255),
ADD COLUMN reset_token_expires TIMESTAMP;

-- Remove columns
ALTER TABLE users
DROP COLUMN IF EXISTS full_name,
DROP COLUMN IF EXISTS role; 