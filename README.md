# HR Data Analysis with LLM

This project provides a natural language interface for HR personnel to analyze employee data stored in a PostgreSQL database. It uses LangChain and OpenAI to process natural language queries and convert them into SQL queries.

## Features

- Natural language processing for database queries
- Predefined HR-related queries for quick access
- Custom query input for flexibility
- Real-time SQL query generation and execution
- Interactive web interface using Streamlit

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL database
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hr-llm-analysis.git
cd hr-llm-analysis
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
   - Create a PostgreSQL database named `hr_database`
   - Run the SQL scripts in the `database` folder:
     ```bash
     psql -U postgres -d hr_database -f database/create_schema.sql
     psql -U postgres -d hr_database -f database/sample_data.sql
     ```

5. Configure environment variables:
   - Copy the `.env.example` file to `.env`
   - Update the values in the `.env` file with your OpenAI API key and database credentials

### Running the Application

Start the Streamlit application:
```bash
streamlit run app.py
```

The application will be available at http://localhost:8501

## Usage

1. Click on any of the predefined queries in the left sidebar
2. Or enter a custom query in the text area
3. View the generated SQL query and results

## Example Queries

- "List all employees in the Engineering department"
- "Show me employees who were absent last week"
- "What is the average salary by department?"
- "Who has the highest attendance rate this month?"
```

## How to Run the Project

1. First, set up your PostgreSQL database:

```bash
createdb hr_database
psql -U postgres -d hr_database -f database/create_schema.sql
psql -U postgres -d hr_database -f database/sample_data.sql
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Update the `.env` file with your OpenAI API key and database credentials.

4. Run the Streamlit application:

```bash
streamlit run app.py
