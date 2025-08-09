import os
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI

# Load environment variables
load_dotenv()

# Get API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

def get_db_uri():
    """Get the database URI from environment variables"""
    import urllib.parse
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "hr_database")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    db_port = os.getenv("DB_PORT", "5432")
    
    # URL-encode the password to handle special characters
    encoded_password = urllib.parse.quote_plus(db_password)
    
    return f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"


def setup_langchain():
    """Set up LangChain with the database"""
    # Create LLM
    llm = OpenAI(temperature=0, api_key=OPENAI_API_KEY)
    
    # Connect to the database
    db_uri = get_db_uri()
    db = SQLDatabase.from_uri(db_uri)

    # Custom prompt template
    _DEFAULT_TEMPLATE = """
    You are an HR data analyst assistant. Given an input question, create a syntactically correct PostgreSQL query to run.

    Use the following information about the database schema:

    Employee Table:
    - employee_id: Primary key
    - first_name, last_name: Employee's name
    - email, phone: Contact information
    - hire_date: When they were hired
    - job_title: Their position
    - department: Which department they work in
    - manager_id: References another employee who is their manager

    Attendance Table:
    - attendance_id: Primary key
    - employee_id: Foreign key to employee
    - date: Date of the attendance record
    - status: 'present', 'absent', 'half-day', or 'leave'
    - check_in, check_out: Time stamps for the day

    Payroll Table:
    - payroll_id: Primary key
    - employee_id: Foreign key to employee
    - month, year: The month and year this payroll is for
    - base_salary: Base salary amount
    - bonus: Additional bonus amount
    - deductions: Amount deducted from salary
    - net_salary: Final salary after bonus and deductions
    - payment_date: When the payment was processed

    Question: {input}

    SQL Query:
    """

    PROMPT = PromptTemplate(
        input_variables=["input"],
        template=_DEFAULT_TEMPLATE
    )

    # Create SQL query chain (updated, correct function)
    db_chain = create_sql_query_chain(llm=llm, db=db, prompt=PROMPT, verbose=True)

    return db_chain
