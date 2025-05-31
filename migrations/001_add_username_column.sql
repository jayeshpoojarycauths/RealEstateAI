-- Add username column (nullable)
ALTER TABLE users ADD COLUMN username VARCHAR;

-- Add comment to the column
COMMENT ON COLUMN users.username IS 'Username for login (initially nullable)'; 