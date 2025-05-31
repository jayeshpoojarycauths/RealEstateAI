-- Update existing users to set username based on email
UPDATE users 
SET username = LOWER(SPLIT_PART(email, '@', 1))
WHERE username IS NULL;

-- Add comment explaining the update
COMMENT ON COLUMN users.username IS 'Username for login (populated from email)'; 