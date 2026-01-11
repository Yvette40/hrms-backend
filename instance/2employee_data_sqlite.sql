
-- Disable foreign key checks temporarily
PRAGMA foreign_keys = OFF;

-- Clear employee table
DELETE FROM employee;

-- Insert 200 sample employees (auto-increment IDs)
INSERT INTO employee (name, national_id, base_salary, active) VALUES
( 'James Ellis', '80379605', 2734.03, FALSE),
( 'Dr. Kimberly Campbell MD', '707418', 3107.04, TRUE),
( 'Melody Smith', '8375272', 4762.16, FALSE),
