-- Sample data for HR database

-- Insert employees
INSERT INTO employee (first_name, last_name, email, phone, hire_date, job_title, department, manager_id)
VALUES
    ('John', 'Smith', 'john.smith@company.com', '555-1234', '2020-01-15', 'Senior Developer', 'Engineering', NULL),
    ('Sarah', 'Johnson', 'sarah.johnson@company.com', '555-2345', '2020-03-10', 'HR Manager', 'Human Resources', NULL),
    ('Michael', 'Williams', 'michael.williams@company.com', '555-3456', '2020-05-20', 'Marketing Specialist', 'Marketing', NULL),
    ('Emily', 'Brown', 'emily.brown@company.com', '555-4567', '2021-02-01', 'Junior Developer', 'Engineering', 1),
    ('David', 'Jones', 'david.jones@company.com', '555-5678', '2021-04-15', 'HR Assistant', 'Human Resources', 2),
    ('Jessica', 'Garcia', 'jessica.garcia@company.com', '555-6789', '2021-06-10', 'Content Creator', 'Marketing', 3),
    ('Daniel', 'Miller', 'daniel.miller@company.com', '555-7890', '2022-01-05', 'DevOps Engineer', 'Engineering', 1),
    ('Lisa', 'Davis', 'lisa.davis@company.com', '555-8901', '2022-03-20', 'Recruiter', 'Human Resources', 2),
    ('Robert', 'Rodriguez', 'robert.rodriguez@company.com', '555-9012', '2022-05-15', 'SEO Specialist', 'Marketing', 3),
    ('Jennifer', 'Martinez', 'jennifer.martinez@company.com', '555-0123', '2023-01-10', 'QA Engineer', 'Engineering', 1);

-- Insert attendance records for the last 7 days
DO $$
DECLARE
    current_date_var DATE := CURRENT_DATE;
    i INTEGER;
    emp_id INTEGER;
    status_var VARCHAR(20);
    check_in_var TIME;
    check_out_var TIME;
BEGIN
    FOR i IN 1..7 LOOP
        FOR emp_id IN 1..10 LOOP
            -- Randomly assign status with 80% present, 10% absent, 10% leave
            IF random() < 0.8 THEN
                status_var := 'present';
                check_in_var := '08:00:00'::TIME + (random() * interval '1 hour');
                check_out_var := '17:00:00'::TIME + (random() * interval '1 hour');
            ELSIF random() < 0.5 THEN
                status_var := 'absent';
                check_in_var := NULL;
                check_out_var := NULL;
            ELSE
                status_var := 'leave';
                check_in_var := NULL;
                check_out_var := NULL;
            END IF;
            
            -- Skip weekends
            IF EXTRACT(DOW FROM (current_date_var - (i || ' days')::INTERVAL)) NOT IN (0, 6) THEN
                INSERT INTO attendance (employee_id, date, status, check_in, check_out)
                VALUES (emp_id, current_date_var - (i || ' days')::INTERVAL, status_var, check_in_var, check_out_var)
                ON CONFLICT (employee_id, date) DO NOTHING;
            END IF;
        END LOOP;
    END LOOP;
END $$;

-- Insert payroll data for the last 4 months
DO $$
DECLARE
    current_month INTEGER := EXTRACT(MONTH FROM CURRENT_DATE);
    current_year INTEGER := EXTRACT(YEAR FROM CURRENT_DATE);
    month_var INTEGER;
    year_var INTEGER;
    emp_id INTEGER;
    base_salary NUMERIC(10, 2);
    bonus NUMERIC(10, 2);
    deductions NUMERIC(10, 2);
    net_salary NUMERIC(10, 2);
    payment_date DATE;
BEGIN
    FOR i IN 1..4 LOOP
        month_var := current_month - i + 1;
        year_var := current_year;
        
        -- Adjust year if we go back to previous year
        IF month_var <= 0 THEN
            month_var := month_var + 12;
            year_var := year_var - 1;
        END IF;
        
        FOR emp_id IN 1..10 LOOP
            -- Base salary based on job role (from employee table)
            SELECT 
                CASE 
                    WHEN job_title LIKE '%Manager%' THEN 8000 + (random() * 2000)
                    WHEN job_title LIKE '%Senior%' THEN 7000 + (random() * 1500)
                    WHEN job_title LIKE '%Engineer%' THEN 6000 + (random() * 1000)
                    WHEN job_title LIKE '%Specialist%' THEN 5000 + (random() * 1000)
                    ELSE 4000 + (random() * 1000)
                END INTO base_salary
            FROM employee WHERE employee_id = emp_id;
            
            -- Random bonus (higher in December - month 12)
            IF month_var = 12 THEN
                bonus := (random() * 1000) + 500;
            ELSE
                bonus := random() * 500;
            END IF;
            
            -- Random deductions
            deductions := (base_salary * 0.2) + (random() * 200);
            
            -- Calculate net salary
            net_salary := base_salary + bonus - deductions;
            
            -- Payment date (15th of the month)
            payment_date := make_date(year_var, month_var, 15);
            
            -- Insert payroll record
            INSERT INTO payroll (employee_id, month, year, base_salary, bonus, deductions, net_salary, payment_date)
            VALUES (emp_id, month_var, year_var, base_salary, bonus, deductions, net_salary, payment_date)
            ON CONFLICT (employee_id, month, year) DO NOTHING;
        END LOOP;
    END LOOP;
END $$;
