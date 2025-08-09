from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import psycopg2
import datetime
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
db_params = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'database': os.getenv('DB_NAME')
}

app = Flask(__name__, static_folder='static')

# Sample predefined queries - replace with your actual queries
PREDEFINED_QUERIES = {
    "employee_info": [
        {"name": "List all employees", "query": "Show me all employees"},
        {"name": "Employees by department", "query": "List employees by department"},
        {"name": "New hires this year", "query": "Show employees hired this year"}
    ],
    "attendance_info": [
        {"name": "Attendance summary", "query": "Show attendance summary for all employees"},
        {"name": "Late arrivals", "query": "List employees who arrived late this month"}
    ],
    "payroll_info": [
        {"name": "Salary breakdown", "query": "Show salary breakdown by department"},
        {"name": "Overtime payments", "query": "List overtime payments this month"},
        {"name": "Insert sample payroll data", "query": "Insert sample payroll data"}
    ]
}

# Function to execute SQL query and return results
def execute_query(query, fetch_results=True):
    conn = None
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        cursor.execute(query)
        
        if not fetch_results:
            conn.commit()
            return [{"message": "Query executed successfully"}]
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Convert results to list of dictionaries
        result_dicts = []
        for row in results:
            result_dict = {}
            for i, column in enumerate(columns):
                # Convert date objects to strings for JSON serialization
                if isinstance(row[i], (datetime.date, datetime.datetime)):
                    result_dict[column] = row[i].isoformat()
                else:
                    result_dict[column] = row[i]
            result_dicts.append(result_dict)
        
        return result_dicts
    except Exception as e:
        print(f"Database error: {e}")
        return [{"error": str(e)}]
    finally:
        if conn:
            conn.close()

# Function to insert sample payroll data
def insert_sample_payroll_data():
    # First, check if there's already data
    check_query = "SELECT COUNT(*) as count FROM payroll"
    result = execute_query(check_query)
    
    if result[0]['count'] > 0:
        return [{"message": "Payroll data already exists"}]
    
    # Insert sample payroll data for all employees
    insert_query = """
    INSERT INTO payroll (employee_id, month, year, base_salary, bonus, deductions, net_salary, payment_date)
    SELECT
        e.employee_id,
        EXTRACT(MONTH FROM CURRENT_DATE)::integer as month,
        EXTRACT(YEAR FROM CURRENT_DATE)::integer as year,
        CASE
            WHEN e.job_title LIKE '%Manager%' THEN 8000
            WHEN e.job_title LIKE '%Senior%' THEN 7000
            WHEN e.job_title LIKE '%Engineer%' THEN 6000
            ELSE 5000
        END as base_salary,
        CASE
            WHEN e.job_title LIKE '%Manager%' THEN 1000
            WHEN e.job_title LIKE '%Senior%' THEN 800
            WHEN e.job_title LIKE '%Engineer%' THEN 600
            ELSE 400
        END as bonus,
        CASE
            WHEN e.job_title LIKE '%Manager%' THEN 2000
            WHEN e.job_title LIKE '%Senior%' THEN 1800
            WHEN e.job_title LIKE '%Engineer%' THEN 1600
            ELSE 1400
        END as deductions,
        CASE
            WHEN e.job_title LIKE '%Manager%' THEN 7000
            WHEN e.job_title LIKE '%Senior%' THEN 6000
            WHEN e.job_title LIKE '%Engineer%' THEN 5000
            ELSE 4000
        END as net_salary,
        CURRENT_DATE as payment_date
    FROM employee e
    ON CONFLICT (employee_id, month, year) DO NOTHING;
    
    -- Insert data for previous month as well
    INSERT INTO payroll (employee_id, month, year, base_salary, bonus, deductions, net_salary, payment_date)
    SELECT
        e.employee_id,
        CASE
            WHEN EXTRACT(MONTH FROM CURRENT_DATE) = 1 THEN 12
            ELSE EXTRACT(MONTH FROM CURRENT_DATE) - 1
        END::integer as month,
        CASE
            WHEN EXTRACT(MONTH FROM CURRENT_DATE) = 1 THEN EXTRACT(YEAR FROM CURRENT_DATE) - 1
            ELSE EXTRACT(YEAR FROM CURRENT_DATE)
        END::integer as year,
        CASE
            WHEN e.job_title LIKE '%Manager%' THEN 8000
            WHEN e.job_title LIKE '%Senior%' THEN 7000
            WHEN e.job_title LIKE '%Engineer%' THEN 6000
            ELSE 5000
        END as base_salary,
        CASE
            WHEN e.job_title LIKE '%Manager%' THEN 1000
            WHEN e.job_title LIKE '%Senior%' THEN 800
            WHEN e.job_title LIKE '%Engineer%' THEN 600
            ELSE 400
        END as bonus,
        CASE
            WHEN e.job_title LIKE '%Manager%' THEN 2000
            WHEN e.job_title LIKE '%Senior%' THEN 1800
            WHEN e.job_title LIKE '%Engineer%' THEN 1600
            ELSE 1400
        END as deductions,
        CASE
            WHEN e.job_title LIKE '%Manager%' THEN 7000
            WHEN e.job_title LIKE '%Senior%' THEN 6000
            WHEN e.job_title LIKE '%Engineer%' THEN 5000
            ELSE 4000
        END as net_salary,
        (CURRENT_DATE - INTERVAL '1 month')::date as payment_date
    FROM employee e
    ON CONFLICT (employee_id, month, year) DO NOTHING;
    """
    
    execute_query(insert_query, fetch_results=False)
    return [{"message": "Sample payroll data has been inserted"}]

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/predefined_queries', methods=['GET'])
def get_predefined_queries():
    return jsonify(PREDEFINED_QUERIES)

@app.route('/api/process_query', methods=['POST'])
def process_query():
    data = request.json
    query = data.get('query', '').lower()
    
    # Process the query and determine what SQL to run
    sql_query = ""
    result = []
    
    # Handle predefined queries directly with exact matches
    if query == "show me all employees":
        sql_query = "SELECT employee_id, first_name, last_name, email, phone, hire_date, job_title, department FROM employee ORDER BY employee_id"
        result = execute_query(sql_query)
    
    elif query == "list employees by department":
        sql_query = """
        SELECT department, COUNT(*) as employee_count,
               STRING_AGG(first_name || ' ' || last_name, ', ') as employees
        FROM employee
        GROUP BY department
        ORDER BY department
        """
        result = execute_query(sql_query)
    
    elif query == "show employees hired this year":
        sql_query = """
        SELECT employee_id, first_name, last_name, hire_date, job_title, department
        FROM employee
        WHERE EXTRACT(YEAR FROM hire_date) = EXTRACT(YEAR FROM CURRENT_DATE)
        ORDER BY hire_date DESC
        """
        result = execute_query(sql_query)
    
    elif query == "show attendance summary for all employees":
        sql_query = """
        SELECT e.employee_id, e.first_name, e.last_name, e.department,
               COUNT(CASE WHEN a.status = 'present' THEN 1 END) as days_present,
               COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as days_absent,
               COUNT(CASE WHEN a.status = 'leave' THEN 1 END) as days_leave
        FROM employee e
        LEFT JOIN attendance a ON e.employee_id = a.employee_id
        GROUP BY e.employee_id, e.first_name, e.last_name, e.department
        ORDER BY e.department, e.last_name
        """
        result = execute_query(sql_query)
    
    elif query == "list employees who arrived late this month":
        sql_query = """
        SELECT e.first_name, e.last_name, a.date, a.check_in
        FROM employee e
        JOIN attendance a ON e.employee_id = a.employee_id
        WHERE a.check_in > '09:00:00' AND a.status = 'present'
        AND EXTRACT(MONTH FROM a.date) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM a.date) = EXTRACT(YEAR FROM CURRENT_DATE)
        ORDER BY a.date DESC, a.check_in DESC
        """
        result = execute_query(sql_query)
    
    elif query == "show salary breakdown by department":
        # First check if payroll data exists
        check_query = "SELECT COUNT(*) as count FROM payroll"
        check_result = execute_query(check_query)
        
        # If no payroll data, insert sample data first
        if check_result[0]['count'] == 0:
            insert_sample_payroll_data()
        
        sql_query = """
        SELECT
            e.department,
            ROUND(AVG(p.base_salary)::numeric, 2) as avg_base_salary,
            ROUND(AVG(p.bonus)::numeric, 2) as avg_bonus,
            ROUND(AVG(p.net_salary)::numeric, 2) as avg_net_salary,
            COUNT(DISTINCT e.employee_id) as employee_count
        FROM
            employee e
        JOIN
            payroll p ON e.employee_id = p.employee_id
        GROUP BY
            e.department
        ORDER BY
            avg_net_salary DESC
        """
        result = execute_query(sql_query)
    
    elif query == "list overtime payments this month":
        # First check if payroll data exists
        check_query = "SELECT COUNT(*) as count FROM payroll"
        check_result = execute_query(check_query)
        
        # If no payroll data, insert sample data first
        if check_result[0]['count'] == 0:
            insert_sample_payroll_data()
        
        sql_query = """
        SELECT
            e.first_name,
            e.last_name,
            e.department,
            p.bonus as overtime_amount,
            p.month,
            p.year
        FROM
            employee e
        JOIN
            payroll p ON e.employee_id = p.employee_id
        WHERE
            p.bonus > 0
            AND p.month = EXTRACT(MONTH FROM CURRENT_DATE)
            AND p.year = EXTRACT(YEAR FROM CURRENT_DATE)
        ORDER BY
            p.bonus DESC
        """
        result = execute_query(sql_query)
    
    elif query == "insert sample payroll data":
        result = insert_sample_payroll_data()
        sql_query = "INSERT INTO payroll ... (sample data)"
    
    else:
        # For custom queries, use the existing NLP logic
        # Extract department if mentioned in the query
        department_match = re.search(r'(engineering|marketing|human resources|hr)', query, re.IGNORECASE)
        department = None
        if department_match:
            dept = department_match.group(1).lower()
            if dept == 'hr':
                department = 'Human Resources'
            else:
                department = dept.title()
        
        # Extract employee name if mentioned
        employee_name_match = re.search(r'(for|about|of|by)\s+([a-z]+\s+[a-z]+)', query, re.IGNORECASE)
        employee_name = None
        if employee_name_match:
            employee_name = employee_name_match.group(2)
        
        # Extract time period if mentioned
        time_period = None
        if "this month" in query or "current month" in query:
            time_period = "current_month"
        elif "last month" in query or "previous month" in query:
            time_period = "last_month"
        elif "this year" in query or "current year" in query:
            time_period = "current_year"
        elif "last year" in query or "previous year" in query:
            time_period = "last_year"
        
        # List all employees
        if ("show" in query or "list" in query or "get" in query) and "employees" in query:
            if department:
                sql_query = f"""
                SELECT employee_id, first_name, last_name, email, phone, hire_date, job_title, department
                FROM employee
                WHERE LOWER(department) = LOWER('{department}')
                ORDER BY employee_id
                """
            else:
                sql_query = "SELECT employee_id, first_name, last_name, email, phone, hire_date, job_title, department FROM employee ORDER BY employee_id"
            result = execute_query(sql_query)
        
        # Employees by department
        elif "department" in query and ("breakdown" in query or "distribution" in query or "count" in query):
            if department:
                sql_query = f"""
                SELECT department, COUNT(*) as employee_count,
                       STRING_AGG(first_name || ' ' || last_name, ', ') as employees
                FROM employee
                WHERE LOWER(department) = LOWER('{department}')
                GROUP BY department
                """
            else:
                sql_query = """
                SELECT department, COUNT(*) as employee_count,
                       STRING_AGG(first_name || ' ' || last_name, ', ') as employees
                FROM employee
                GROUP BY department
                ORDER BY department
                """
            result = execute_query(sql_query)
        
        # Information about a specific department
        # Information about a specific department
        elif any(x in query for x in ["information", "info", "details", "data"]) and department:
            sql_query = f"""
            SELECT e.department,
                   COUNT(DISTINCT e.employee_id) as employee_count,
                   STRING_AGG(DISTINCT e.job_title, ', ') as job_titles,
                   ROUND(AVG(p.base_salary)::numeric, 2) as avg_salary
            FROM employee e
            LEFT JOIN payroll p ON e.employee_id = p.employee_id
            WHERE LOWER(e.department) = LOWER('{department}')
            GROUP BY e.department
            """
            result = execute_query(sql_query)
        
        # New hires
        elif "hire" in query or "new employee" in query:
            time_condition = ""
            if time_period == "current_year":
                time_condition = "EXTRACT(YEAR FROM hire_date) = EXTRACT(YEAR FROM CURRENT_DATE)"
            elif time_period == "last_year":
                time_condition = "EXTRACT(YEAR FROM hire_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1"
            elif time_period == "current_month":
                time_condition = "EXTRACT(YEAR FROM hire_date) = EXTRACT(YEAR FROM CURRENT_DATE) AND EXTRACT(MONTH FROM hire_date) = EXTRACT(MONTH FROM CURRENT_DATE)"
            
            if department and time_condition:
                sql_query = f"""
                SELECT employee_id, first_name, last_name, hire_date, job_title, department
                FROM employee
                WHERE LOWER(department) = LOWER('{department}') AND {time_condition}
                ORDER BY hire_date DESC
                """
            elif department:
                sql_query = f"""
                SELECT employee_id, first_name, last_name, hire_date, job_title, department
                FROM employee
                WHERE LOWER(department) = LOWER('{department}')
                ORDER BY hire_date DESC
                LIMIT 5
                """
            elif time_condition:
                sql_query = f"""
                SELECT employee_id, first_name, last_name, hire_date, job_title, department
                FROM employee
                WHERE {time_condition}
                ORDER BY hire_date DESC
                """
            else:
                sql_query = """
                SELECT employee_id, first_name, last_name, hire_date, job_title, department
                FROM employee
                ORDER BY hire_date DESC
                LIMIT 5
                """
            result = execute_query(sql_query)
        
        # Attendance summary
        elif "attendance" in query:
            if department:
                sql_query = f"""
                SELECT e.employee_id, e.first_name, e.last_name, e.department,
                       COUNT(CASE WHEN a.status = 'present' THEN 1 END) as days_present,
                       COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as days_absent,
                       COUNT(CASE WHEN a.status = 'leave' THEN 1 END) as days_leave
                FROM employee e
                LEFT JOIN attendance a ON e.employee_id = a.employee_id
                WHERE LOWER(e.department) = LOWER('{department}')
                GROUP BY e.employee_id, e.first_name, e.last_name, e.department
                ORDER BY e.department, e.last_name
                """
            elif employee_name:
                names = employee_name.split()
                if len(names) >= 2:
                    first_name, last_name = names[0], names[1]
                    sql_query = f"""
                    SELECT e.employee_id, e.first_name, e.last_name, e.department,
                           COUNT(CASE WHEN a.status = 'present' THEN 1 END) as days_present,
                           COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as days_absent,
                           COUNT(CASE WHEN a.status = 'leave' THEN 1 END) as days_leave
                    FROM employee e
                    LEFT JOIN attendance a ON e.employee_id = a.employee_id
                    WHERE LOWER(e.first_name) LIKE LOWER('%{first_name}%') AND LOWER(e.last_name) LIKE LOWER('%{last_name}%')
                    GROUP BY e.employee_id, e.first_name, e.last_name, e.department
                    """
                else:
                    sql_query = f"""
                    SELECT e.employee_id, e.first_name, e.last_name, e.department,
                           COUNT(CASE WHEN a.status = 'present' THEN 1 END) as days_present,
                           COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as days_absent,
                           COUNT(CASE WHEN a.status = 'leave' THEN 1 END) as days_leave
                    FROM employee e
                    LEFT JOIN attendance a ON e.employee_id = a.employee_id
                    WHERE LOWER(e.first_name) LIKE LOWER('%{employee_name}%') OR LOWER(e.last_name) LIKE LOWER('%{employee_name}%')
                    GROUP BY e.employee_id, e.first_name, e.last_name, e.department
                    """
            else:
                sql_query = """
                SELECT e.employee_id, e.first_name, e.last_name, e.department,
                       COUNT(CASE WHEN a.status = 'present' THEN 1 END) as days_present,
                       COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as days_absent,
                       COUNT(CASE WHEN a.status = 'leave' THEN 1 END) as days_leave
                FROM employee e
                LEFT JOIN attendance a ON e.employee_id = a.employee_id
                GROUP BY e.employee_id, e.first_name, e.last_name, e.department
                ORDER BY e.department, e.last_name
                """
            result = execute_query(sql_query)
        
        # Late arrivals
        elif "late" in query:
            if department:
                sql_query = f"""
                SELECT e.first_name, e.last_name, a.date, a.check_in
                FROM employee e
                JOIN attendance a ON e.employee_id = a.employee_id
                WHERE a.check_in > '09:00:00' AND a.status = 'present' AND LOWER(e.department) = LOWER('{department}')
                ORDER BY a.date DESC, a.check_in DESC
                """
            else:
                sql_query = """
                SELECT e.first_name, e.last_name, a.date, a.check_in
                FROM employee e
                JOIN attendance a ON e.employee_id = a.employee_id
                WHERE a.check_in > '09:00:00' AND a.status = 'present'
                ORDER BY a.date DESC, a.check_in DESC
                """
            result = execute_query(sql_query)
        
        # Salary breakdown by department
        elif "salary" in query or "payroll" in query:
            # First check if payroll data exists
            check_query = "SELECT COUNT(*) as count FROM payroll"
            check_result = execute_query(check_query)
            
            # If no payroll data, insert sample data first
            if check_result[0]['count'] == 0:
                insert_sample_payroll_data()
            
            if department:
                sql_query = f"""
                SELECT
                    e.department,
                    ROUND(AVG(p.base_salary)::numeric, 2) as avg_base_salary,
                    ROUND(AVG(p.bonus)::numeric, 2) as avg_bonus,
                    ROUND(AVG(p.net_salary)::numeric, 2) as avg_net_salary,
                    COUNT(DISTINCT e.employee_id) as employee_count
                FROM
                    employee e
                JOIN
                    payroll p ON e.employee_id = p.employee_id
                WHERE LOWER(e.department) = LOWER('{department}')
                GROUP BY
                    e.department
                """
            else:
                sql_query = """
                SELECT
                    e.department,
                    ROUND(AVG(p.base_salary)::numeric, 2) as avg_base_salary,
                    ROUND(AVG(p.bonus)::numeric, 2) as avg_bonus,
                    ROUND(AVG(p.net_salary)::numeric, 2) as avg_net_salary,
                    COUNT(DISTINCT e.employee_id) as employee_count
                FROM
                    employee e
                JOIN
                    payroll p ON e.employee_id = p.employee_id
                GROUP BY
                    e.department
                ORDER BY
                    avg_net_salary DESC
                """
            result = execute_query(sql_query)
        
        # Overtime payments
        elif "overtime" in query or "bonus" in query:
            # First check if payroll data exists
            check_query = "SELECT COUNT(*) as count FROM payroll"
            check_result = execute_query(check_query)
            
            # If no payroll data, insert sample data first
            if check_result[0]['count'] == 0:
                insert_sample_payroll_data()
            
            if department:
                sql_query = f"""
                SELECT
                    e.first_name,
                    e.last_name,
                    e.department,
                    p.bonus as overtime_amount,
                    p.month,
                    p.year
                FROM
                    employee e
                JOIN
                    payroll p ON e.employee_id = p.employee_id
                WHERE
                    p.bonus > 0 AND LOWER(e.department) = LOWER('{department}')
                ORDER BY
                    p.bonus DESC
                """
            else:
                sql_query = """
                SELECT
                    e.first_name,
                    e.last_name,
                    e.department,
                    p.bonus as overtime_amount,
                    p.month,
                    p.year
                FROM
                    employee e
                JOIN
                    payroll p ON e.employee_id = p.employee_id
                WHERE
                    p.bonus > 0
                ORDER BY
                    p.bonus DESC
                """
            result = execute_query(sql_query)
        
        # Default query if nothing specific is matched
        else:
            if department:
                sql_query = f"""
                SELECT employee_id, first_name, last_name, email, phone, hire_date, job_title, department
                FROM employee
                WHERE LOWER(department) = LOWER('{department}')
                ORDER BY employee_id
                """
            else:
                sql_query = "SELECT * FROM employee LIMIT 10"
            result = execute_query(sql_query)
    
    return jsonify({
        "success": True,
        "sql_query": sql_query,
        "result": result
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
