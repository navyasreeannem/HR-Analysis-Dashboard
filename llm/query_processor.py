from langchain_setup import setup_langchain


class QueryProcessor:
    def __init__(self):
        self.db_chain = setup_langchain()
    
    def process_query(self, query):
        """Process a natural language query and return the results"""
        try:
            # The newer chain structure returns different output
            result = self.db_chain.invoke({"question": query})
            
            # Extract the SQL query and result
            return {
                'sql_query': result.get("sql_query", "SQL query not available"),
                'result': result.get("result", result),
                'error': None
            }
        except Exception as e:
            return {
                'sql_query': None,
                'result': None,
                'error': str(e)
            }
