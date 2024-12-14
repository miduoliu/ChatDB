import random

DATABASE_SCHEMA = {
    "ChatDB": {
        "tables": {
            "customers": {
                "categorical": ["customer_id", "customer_unique_id", "customer_city", "customer_state"],
                "numerical": ["customer_zip_code_prefix"]
            },
            "orders": {
                "categorical": [
                    "order_id",
                    "customer_id",
                    "order_status"
                ],
                "numerical": [
                    "order_purchase_timestamp",
                    "order_approved_at",
                    "order_delivered_carrier_date",
                    "order_delivered_customer_date",
                    "order_estimated_delivery_date"
                ]
            },
            "payments": {
                "categorical": ["order_id", "payment_type"],
                "numerical": ["payment_sequential", "payment_installments", "payment_value"]
            }
        }
    }
}

def generate_sql_query(pattern, table_name, columns, join_info=None):
    """Generate SQL queries based on patterns and constructs."""
    if pattern == "total <A> by <B>":
        return f"""
        SELECT {columns[1]}, SUM({columns[0]}) AS total_{columns[0]}
        FROM {table_name}
        GROUP BY {columns[1]};
        """
    elif pattern == "average <A> by <B> where <C> > <value>":
        return f"""
        SELECT {columns[1]}, AVG({columns[0]}) AS avg_{columns[0]}
        FROM {table_name}
        WHERE {columns[2]} > 50
        GROUP BY {columns[1]};
        """
    elif pattern == "list all <A> ordered by <B>":
        return f"""
        SELECT *
        FROM {table_name}
        ORDER BY {columns[0]} DESC;
        """
    elif pattern == "find max <A>":
        return f"""
        SELECT MAX({columns[0]}) AS max_{columns[0]}
        FROM {table_name};
        """
    elif pattern == "find <A> from <table1> joined with <table2> on <condition>":
        if join_info:
            table1, table2, condition = join_info
            return f"""
            SELECT {columns[0]}
            FROM {table1}
            JOIN {table2}
            ON {condition};
            """
    return "Query pattern not recognized."

def generate_group_by_query(table_name, columns):
    """Generate sample queries using GROUP BY based on table schema."""
    queries = []

    if len(columns) < 2:
        # Skip if not enough columns for meaningful queries
        return queries

    queries.append({
        "description": f"Total {columns[1]} by {columns[0]}",
        "sql": f"""
            SELECT {columns[0]}, SUM({columns[1]}) AS total_{columns[1]}
            FROM {table_name}
            GROUP BY {columns[0]};
        """
    })

    queries.append({
        "description": f"Average {columns[1]} by {columns[0]}",
        "sql": f"""
            SELECT {columns[0]}, AVG({columns[1]}) AS avg_{columns[1]}
            FROM {table_name}
            GROUP BY {columns[0]};
        """
    })

    queries.append({
        "description": f"Count of {columns[1]} by {columns[0]}",
        "sql": f"""
            SELECT {columns[0]}, COUNT({columns[1]}) AS count_{columns[1]}
            FROM {table_name}
            GROUP BY {columns[0]};
        """
    })

    return queries

def generate_sample_queries(table_name, schema, num_queries=3):
    """
    Generate SQL sample queries using random columns from the schema.
    
    Args:
        table_name (str): The table name to query.
        schema (dict): The schema with categorical and numerical columns.
        num_queries (int): Number of queries to generate.
    
    Returns:
        List of query descriptions and SQL queries.
    """
    query_patterns = {
        "total <A> in <table>": "SELECT SUM({A}) AS total_{A} FROM {table}",
        "maximum <A> in <table>": "SELECT MAX({A}) AS max_{A} FROM {table}",
        "the order of <A> in <table>": "SELECT {A} FROM {table} ORDER BY {A} DESC",
        "minimum <A> in <table>": "SELECT MIN({A}) AS min_{A} FROM {table}",
        "average <A> in <table>": "SELECT AVG({A}) AS avg_{A} FROM {table}",
        "count of <A> grouped by <B>": "SELECT {B}, COUNT({A}) AS count_{A} FROM {table} GROUP BY {B}"
    }

    numerical_columns = schema['numerical']
    categorical_columns = schema['categorical']
    sample_queries = []

    for i in range(num_queries):
        pattern = random.choice(list(query_patterns.keys()))
        query_template = query_patterns[pattern]
        
        A = random.choice(numerical_columns if numerical_columns else categorical_columns)
        B = random.choice(categorical_columns) if '<B>' in pattern else ''
        value = 'example_value' if '<value>' in pattern else ''
        
        query_description = pattern.replace('<A>', A).replace('<B>', B).replace('<table>', table_name).replace('<value>', value)
        sql_query = query_template.format(A=A, B=B, table=table_name, value=value)
        
        sample_queries.append({
            'description': query_description,
            'sql': sql_query
        })
    
    return sample_queries