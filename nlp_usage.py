import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np


nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))
pattern = None

# DATABASE_SCHEMA = {
#     "ChatDB": {
#         "tables": {
#             "customers": {
#                 "categorical": ["customer_id", "customer_unique_id", "customer_city", "customer_state"],
#                 "numerical": ["customer_zipcode", "customer_age"]
#             },
#             "orders": {
#                 "categorical": [
#                     "order_id",
#                     "customer_id",
#                     "order_status"
#                 ],
#                 "numerical": [
#                     "order_cost",
#                     "order_time",
#                     "order_rates",
#                     "order_tips"
#                 ]
#             },
#             "payments": {
#                 "categorical": ["order_id", "payment_type"],
#                 "numerical": ["payment_sequential", "payment_installments", "payment_value"]
#             }
#         }
#     }
# }

# Query patterns and templates
QUERY_PATTERNS = {
    "find all <A> where <B> = <value>": "SELECT * FROM {table1} WHERE {attribute1} = '{value}'",
    "show total <A> in <B>": "SELECT SUM({attribute1}) as total_{attribute1} FROM {table1}",
    "show average <A> by <B>": "SELECT AVG({attribute1}) AS avg_{attribute1} FROM {table1}",
    "list all <A> ordered by <B>": "SELECT {attribute1} FROM {table1} ORDER BY {attribute1} DESC",
    "show number of <A> by <B>": "SELECT COUNT({attribute1}) AS count_{attribute1} FROM {table1}",
    "find max <A>": "SELECT MAX({attribute1}) AS max_{attribute1} FROM {table1}",
    "inner join <A> and <B>": "SELECT * FROM {table1} INNER JOIN {table2} ON {table1}.{attribute1} = {table2}.{attribute2}"
}

# Step 1: Preprocess Query
def preprocess_query(input_query):
    """Preprocess the natural language query: tokenize, lemmatize, and remove stopwords."""
    tokens = word_tokenize(input_query.lower())
    # stop_words.remove("by")
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return tokens

# Step 2: Match Query Pattern
def match_query_pattern(tokens):
    """Match tokens to a predefined query pattern."""
    if "find" in tokens:
        return "find all <A> where <B> = <value>"
    elif "total" in tokens:
        return "show total <A> in <B>"
    elif "average" in tokens:
        return "show average <A> by <B>"
    elif "list" in tokens:
        return "list all <A> ordered by <B>"
    elif "many" in tokens:
        return "show number of <A> by <B>"
    elif "maximum" in tokens:
        return "find max <A>"
    elif len(set(tokens)) > 1:
        return "inner join <A> and <B>"
    return None

def fuzzy_match_by_substring(token, candidates):
    """
    Match a token against a list of candidates using substring matching.

    Args:
        token (str): The token to match.
        candidates (list): A list of candidate strings.

    Returns:
        str: The first candidate that contains the token as a substring, or None if no match is found.
    """
    token_lower = token.lower()
    for candidate in candidates:
        if token_lower in candidate.lower():
            return candidate
    return None

def classify_attributes(cursor, table):
    """
    Classify attributes of a table into categorical and numerical columns using SQL DESCRIBE.

    Args:
        cursor: The MySQL cursor object.
        table (str): The table name.
    
    Returns:
        dict: Dictionary with "categorical" and "numerical" keys containing lists of attributes.
    """
    cursor.execute(f"DESCRIBE {table}")
    rows = cursor.fetchall()
    categorical = []
    numerical = []
    for row in rows:
        column_name = row[0]
        data_type = row[1].lower()
        if "int" in data_type or "float" in data_type or "double" in data_type or "decimal" in data_type:
            numerical.append(column_name)
        else:
            categorical.append(column_name)
    return {"categorical": categorical, "numerical": numerical}

def identify_entities(pattern, tokens, cursor, current_database):
    """
    Identify table, attributes, and values from tokens using fuzzy matching.
    
    Args:
        tokens (list): Tokenized input query.
        schema (dict): The database schema.
    
    Returns:
        tuple: (table, attribute, value) if identified, otherwise None.
    """
    if not current_database:
        print("No database selected.")
        return None, None, None, None, None

    # Set the database context
    cursor.execute(f"USE {current_database}")

    table1 = None
    table2 = None
    attribute1 = None
    attribute2 = None
    value = None
    
    # Step 1: Identify table
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    matched_tables = []

    if pattern == "inner join <A> and <B>":
        for token in tokens:
            match = fuzzy_match_by_substring(token, tables)
            if match and match not in matched_tables:
                matched_tables.append(match)
                # tokens.remove(token)
            if len(matched_tables) == 2:
                break

    
        if matched_tables:
            table1 = matched_tables[0]
            if len(matched_tables) > 1:
                table2 = matched_tables[1]

        # Step 2: Identify attributes
        attributes1, attributes2 = [], []
        if table1:
            attributes1 = classify_attributes(cursor, table1)["categorical"] + classify_attributes(cursor, table1)["numerical"]
        if table2:
            attributes2 = classify_attributes(cursor, table2)["categorical"] + classify_attributes(cursor, table2)["numerical"]

        for token in tokens:
            if table1 and not attribute1:
                match = fuzzy_match_by_substring(token, attributes1)
                if match:
                    attribute1 = match
                    # tokens.remove(token)
            if table2 and not attribute2:
                match = fuzzy_match_by_substring(token, attributes2)
                if match:
                    attribute2 = match
                    # tokens.remove(token)
        # print("Table: ", table)
        # print("Attribute: ", attribute)
        # cursor.execute(f"SELECT DISTINCT {attribute} FROM {table}")
        # Step 3: Identify value (tokens not matching table or attributes)
    else:
        for token in tokens:
            match = fuzzy_match_by_substring(token, tables)
            if match:
                table1 = match
                tokens.remove(token)
                break

    # Step 2: Identify attributes
        if table1:
            attributes_info = classify_attributes(cursor, table1)
            attributes = attributes_info["categorical"] + attributes_info["numerical"]
            for token in tokens:
                match = fuzzy_match_by_substring(token, attributes)
                if match:
                    attribute1 = match
                    tokens.remove(token)
                    break
        
        # Step 3: Identify value (tokens not matching table or attributes)
        if table1 and attribute1:
            cursor.execute(f"SELECT DISTINCT {attribute1} FROM {table1}")
            attribute_values = [str(row[0]).lower() for row in cursor.fetchall()]
            for token in tokens:
                if token.lower() in attribute_values:
                    value = token
                    tokens.remove(token)
                    break

    return table1, table2, attribute1, attribute2, value
# Step 3: Generate SQL Query
def generate_sql_query_from_nl(pattern, table1, table2, attribute1, attribute2, value):
    """Generate SQL query based on the matched pattern."""
    if pattern not in QUERY_PATTERNS:
        return None

    sql_template = QUERY_PATTERNS[pattern]
    # table_schema = schema["ChatDB"]["tables"][table]
    # categorical = table_schema["categorical"]
    # numerical = table_schema["numerical"]

    # sql_template = QUERY_PATTERNS[pattern]
    return sql_template.format(table1=table1, table2=table2, attribute1=attribute1, attribute2=attribute2, value=value)
    # Dynamically populate placeholders based on the pattern
    # if pattern == "find all <A> where <B> = <value>":
    #     field = categorical[0]  # Default field for simplicity
    #     value = input(f"Enter value for {field}: ").strip()
    #     return sql_template.format(A="*", B=field, value=value, table=table)
    # elif pattern == "show total <A> by <B>":
    #     return sql_template.format(A=numerical[0], B=categorical[0], table=table)
    # elif pattern == "show average <A> by <B>":
    #     return sql_template.format(A=numerical[0], B=categorical[0], table=table)
    # elif pattern == "list all <A> ordered by <B>":
    #     return sql_template.format(A="*", B=categorical[0], table=table)
    # elif pattern == "show number of <A> by <B>":
    #     return sql_template.format(A="*", B=categorical[0], table=table)
    # elif pattern == "find max <A>":
    #     return sql_template.format(A=numerical[0], table=table)

    # return None



# Step 4: Execute Natural Language Query
# def execute_nl_query(cursor, schema, current_database):
#     """Process and execute a natural language query."""

#     if not current_database:
#         print("Please select a database first.")
#         return

#     # Set the database
#     cursor.execute(f"USE {current_database}")
#     user_query = input("\nEnter your query in natural language: ").strip()
#     tokens = preprocess_query(user_query)
#     print("Tokens:", tokens)  # Debugging

#     # Step 1: Match pattern
#     pattern = match_query_pattern(tokens)
#     if not pattern:
#         print("Could not match your query to any known patterns. Please try again.")
#         return

#     # Step 2: Identify entities (table, attribute, value)
#     table, attribute, value = identify_entities(tokens, schema, cursor, current_database)
#     if not table or not attribute or not value:
#         print("Could not identify necessary entities (table, attribute, or value).")
#         return

#     # Step 3: Generate SQL query
#     sql_query = generate_sql_query_from_nl(pattern, table, attribute, value)
#     if not sql_query:
#         print("Could not generate a valid SQL query. Please refine your query.")
#         return

#     print(f"\nExecuting Query:\n{sql_query}")
#     try:
#         cursor.execute(sql_query)
#         results = cursor.fetchall()
#         for row in results[:5]:  # Show only the first 5 rows
#             print(row)
#     except Exception as e:
#         print(f"Error executing query: {e}")
