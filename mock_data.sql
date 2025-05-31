-- Insert mock customer
INSERT INTO customers (id, name) VALUES 
('11111111-1111-1111-1111-111111111111', 'Demo Real Estate Company');

-- Insert mock permissions
INSERT INTO permissions (id, action, resource) VALUES
('22222222-2222-2222-2222-222222222222', 'create', 'leads'),
('33333333-3333-3333-3333-333333333333', 'read', 'leads'),
('44444444-4444-4444-4444-444444444444', 'update', 'leads'),
('55555555-5555-5555-5555-555555555555', 'delete', 'leads'),
('66666666-6666-6666-6666-666666666666', 'create', 'projects'),
('77777777-7777-7777-7777-777777777777', 'read', 'projects'),
('88888888-8888-8888-8888-888888888888', 'update', 'projects'),
('99999999-9999-9999-9999-999999999999', 'delete', 'projects');

-- Insert mock roles
INSERT INTO roles (id, name, description, customer_id) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Admin', 'Full access to all features', '11111111-1111-1111-1111-111111111111'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Manager', 'Can manage leads and projects', '11111111-1111-1111-1111-111111111111'),
('cccccccc-cccc-cccc-cccc-cccccccccccc', 'Agent', 'Can view and update leads', '11111111-1111-1111-1111-111111111111');

-- Assign permissions to roles
-- Admin role gets all permissions
INSERT INTO role_permissions (role_id, permission_id) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '22222222-2222-2222-2222-222222222222'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '33333333-3333-3333-3333-333333333333'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '44444444-4444-4444-4444-444444444444'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '55555555-5555-5555-5555-555555555555'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '66666666-6666-6666-6666-666666666666'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '77777777-7777-7777-7777-777777777777'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '88888888-8888-8888-8888-888888888888'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '99999999-9999-9999-9999-999999999999');

-- Manager role gets create, read, update permissions
INSERT INTO role_permissions (role_id, permission_id) VALUES
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '22222222-2222-2222-2222-222222222222'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '33333333-3333-3333-3333-333333333333'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '44444444-4444-4444-4444-444444444444'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '66666666-6666-6666-6666-666666666666'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '77777777-7777-7777-7777-777777777777'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '88888888-8888-8888-8888-888888888888');

-- Agent role gets read and update permissions for leads
INSERT INTO role_permissions (role_id, permission_id) VALUES
('cccccccc-cccc-cccc-cccc-cccccccccccc', '33333333-3333-3333-3333-333333333333'),
('cccccccc-cccc-cccc-cccc-cccccccccccc', '44444444-4444-4444-4444-444444444444');

-- Insert mock users (password is 'password123' hashed using bcrypt)
INSERT INTO users (id, email, password_hash, is_active, is_superuser, customer_id) VALUES
('dddddddd-dddd-dddd-dddd-dddddddddddd', 'admin@demo.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I6e', true, true, '11111111-1111-1111-1111-111111111111'),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'manager@demo.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I6e', true, false, '11111111-1111-1111-1111-111111111111'),
('ffffffff-ffff-ffff-ffff-ffffffffffff', 'agent@demo.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I6e', true, false, '11111111-1111-1111-1111-111111111111');

-- Assign roles to users
INSERT INTO user_roles (user_id, role_id) VALUES
('dddddddd-dddd-dddd-dddd-dddddddddddd', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
('ffffffff-ffff-ffff-ffff-ffffffffffff', 'cccccccc-cccc-cccc-cccc-cccccccccccc');

-- Insert communication preferences for the customer
INSERT INTO communication_preferences (customer_id) VALUES
('11111111-1111-1111-1111-111111111111');

-- Insert scraping config for the customer
INSERT INTO scraping_configs (customer_id) VALUES
('11111111-1111-1111-1111-111111111111');
