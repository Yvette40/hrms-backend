-- SQL Script to Update Employee Data with Departments, Positions, and Contact Info
-- Run this script in your database to populate missing fields

-- Update John Mwangi
UPDATE employee 
SET department = 'Engineering',
    position = 'Software Engineer',
    email = 'john.mwangi@glimmer.com',
    phone_number = '+254712345678',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '12345678';

-- Update Mary Wanjiku
UPDATE employee 
SET department = 'Finance',
    position = 'Accountant',
    email = 'mary.wanjiku@glimmer.com',
    phone_number = '+254723456789',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '23456789';

-- Update Peter Omondi
UPDATE employee 
SET department = 'Sales',
    position = 'Sales Manager',
    email = 'peter.omondi@glimmer.com',
    phone_number = '+254734567890',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '34567890';

-- Update Jane Akinyi
UPDATE employee 
SET department = 'Marketing',
    position = 'Marketing Officer',
    email = 'jane.akinyi@glimmer.com',
    phone_number = '+254745678901',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '45678901';

-- Update David Kamau
UPDATE employee 
SET department = 'Engineering',
    position = 'Senior Developer',
    email = 'david.kamau@glimmer.com',
    phone_number = '+254756789012',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '56789012';

-- Update Grace Njeri
UPDATE employee 
SET department = 'HR',
    position = 'HR Assistant',
    email = 'grace.njeri@glimmer.com',
    phone_number = '+254767890123',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '67890123';

-- Update James Otieno
UPDATE employee 
SET department = 'Operations',
    position = 'Operations Manager',
    email = 'james.otieno@glimmer.com',
    phone_number = '+254778901234',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '78901234';

-- Update Lucy Chebet
UPDATE employee 
SET department = 'Finance',
    position = 'Financial Analyst',
    email = 'lucy.chebet@glimmer.com',
    phone_number = '+254789012345',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '89012345';

-- Update Samuel Kipchoge
UPDATE employee 
SET department = 'Sales',
    position = 'Sales Executive',
    email = 'samuel.kipchoge@glimmer.com',
    phone_number = '+254790123456',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '90123456';

-- Update Rose Wambui
UPDATE employee 
SET department = 'Admin',
    position = 'Office Administrator',
    email = 'rose.wambui@glimmer.com',
    phone_number = '+254701234567',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '01234567';

-- Update Patrick Mutua
UPDATE employee 
SET department = 'IT',
    position = 'IT Support Specialist',
    email = 'patrick.mutua@glimmer.com',
    phone_number = '+254711234568',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '11234568';

-- Update Susan Nyambura
UPDATE employee 
SET department = 'Customer Service',
    position = 'Customer Service Representative',
    email = 'susan.nyambura@glimmer.com',
    phone_number = '+254721234569',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '21234569';

-- Update Michael Ochieng
UPDATE employee 
SET department = 'Logistics',
    position = 'Logistics Coordinator',
    email = 'michael.ochieng@glimmer.com',
    phone_number = '+254731234560',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '31234560';

-- Update Ann Muthoni
UPDATE employee 
SET department = 'Legal',
    position = 'Legal Officer',
    email = 'ann.muthoni@glimmer.com',
    phone_number = '+254741234561',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '41234561';

-- Update Robert Kariuki
UPDATE employee 
SET department = 'Procurement',
    position = 'Procurement Officer',
    email = 'robert.kariuki@glimmer.com',
    phone_number = '+254751234562',
    updated_at = CURRENT_TIMESTAMP
WHERE national_id = '51234562';

-- Verify the updates
SELECT 
    id,
    name,
    national_id,
    department,
    position,
    email,
    phone_number,
    base_salary
FROM employee
ORDER BY id;
