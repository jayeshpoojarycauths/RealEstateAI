-- Add unique index on username
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Make username column not null
ALTER TABLE users ALTER COLUMN username SET NOT NULL;

-- Update comment
COMMENT ON COLUMN users.username IS 'Username for login (unique, not null)'; 