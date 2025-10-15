-- Direct SQL commands to manage students
-- Use these in pgAdmin 4 or any PostgreSQL client

-- 1. VIEW ALL STUDENTS
SELECT 
    id,
    name,
    ic_number,
    role,
    balance,
    frozen,
    CASE 
        WHEN pin_hash IS NOT NULL THEN 'Hashed'
        ELSE 'Not Set'
    END as pin_status,
    CASE 
        WHEN password_hash IS NOT NULL THEN 'Hashed'
        ELSE 'Not Set'
    END as password_status
FROM student_info 
ORDER BY name;

-- 2. ADD NEW STUDENT (you'll need to hash the PIN/password manually)
-- Example: Adding a student with IC 1003, PIN 1234
INSERT INTO student_info (name, ic_number, role, balance, frozen, pin_hash, password_hash)
VALUES (
    'New Student Name',
    '1003',
    'student',
    0,
    false,
    '$2b$12$example_hashed_pin_here',  -- You need to generate this hash
    NULL
);

-- 3. UPDATE STUDENT BALANCE
UPDATE student_info 
SET balance = 50 
WHERE ic_number = '1234';

-- 4. FREEZE/UNFREEZE STUDENT
UPDATE student_info 
SET frozen = true 
WHERE ic_number = '1234';

-- 5. CHANGE STUDENT ROLE
UPDATE student_info 
SET role = 'staff' 
WHERE ic_number = '1234';

-- 6. DELETE STUDENT
DELETE FROM student_info 
WHERE ic_number = '1234';

-- 7. RESET STUDENT PIN (you'll need to generate new hash)
UPDATE student_info 
SET pin_hash = '$2b$12$new_hashed_pin_here'
WHERE ic_number = '1234';

-- 8. SEARCH STUDENTS BY NAME
SELECT * FROM student_info 
WHERE name ILIKE '%john%';

-- 9. GET STUDENTS BY ROLE
SELECT * FROM student_info 
WHERE role = 'student';

-- 10. GET STUDENTS WITH LOW BALANCE
SELECT * FROM student_info 
WHERE balance < 10;
