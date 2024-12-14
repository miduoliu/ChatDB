import pandas as pd

def list_databases(cursor):
    """List all databases in MySQL."""
    cursor.execute("SHOW DATABASES;")
    databases = [db[0] for db in cursor.fetchall()]

    # Stop at 'information_schema' if it exists
    if "information_schema" in databases:
        databases = databases[:databases.index("information_schema")]

    return databases

def list_tables(cursor, database):
    """List all tables in the selected database."""
    cursor.execute(f"USE {database}")
    cursor.execute("SHOW TABLES")
    return [table[0] for table in cursor.fetchall()]

def show_table_attributes(cursor, table_name):
    """Show the attributes of a table."""
    cursor.execute(f"DESCRIBE {table_name}")
    return pd.DataFrame(cursor.fetchall(), columns=["Field", "Type", "Null", "Key", "Default", "Extra"])

def show_sample_data(cursor, table_name, limit=5):
    """Display the first `limit` rows of a table."""
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(rows, columns=columns)

def upload_dataset(cursor, conn, table_name):
    """Upload a CSV file into a MySQL table, creating the table if it doesn't exist."""
    # Prompt the user for the file path
    file_path = input("\nEnter the full path to your CSV file: ").strip()
    
    try:
        # Load the CSV file with Pandas to inspect the structure
        data = pd.read_csv(file_path, nrows=1)  # Only load the header row
        
        # Check if the table exists
        cursor.execute("SHOW TABLES;")
        tables = [table[0] for table in cursor.fetchall()]
        if table_name not in tables:
            print(f"Table '{table_name}' does not exist. Creating the table...")
            create_table_from_csv(cursor, table_name, data)
            print(f"Table '{table_name}' created successfully!")
        
        # Upload the data using LOAD DATA LOCAL INFILE
        file_path = file_path.replace("\\", "/")
        query = f"""
        LOAD DATA LOCAL INFILE '{file_path}'
        INTO TABLE {table_name}
        FIELDS TERMINATED BY ',' 
        ENCLOSED BY '"'
        LINES TERMINATED BY '\\n'
        IGNORE 1 ROWS;
        """
        cursor.execute(query)
        conn.commit()
        print(f"Data from {file_path} uploaded successfully into {table_name}!")
    except Exception as e:
        print(f"Error uploading dataset: {e}")

def create_table_from_csv(cursor, table_name, data):
    """Create a MySQL table dynamically based on the CSV structure."""
    columns = []
    for col, dtype in data.dtypes.items():
        if dtype == 'int64':
            col_type = "INT"
        elif dtype == 'float64':
            col_type = "FLOAT"
        else:
            col_type = "VARCHAR(255)"  # Default to string for non-numeric types
        columns.append(f"`{col}` {col_type}")
    
    # Construct the CREATE TABLE query
    columns_sql = ", ".join(columns)
    create_table_query = f"CREATE TABLE `{table_name}` ({columns_sql});"
    
    # Execute the query
    cursor.execute(create_table_query)

def insert_record(cursor, conn, table_name):
    """Insert a record into the specified table."""
    # Get table schema
    cursor.execute(f"DESCRIBE {table_name}")
    columns = [row[0] for row in cursor.fetchall()]
    print(f"\nColumns in {table_name}: {', '.join(columns)}")

    # Get values for each column
    values = []
    for column in columns:
        value = input(f"Enter value for {column} (or press Enter to skip): ").strip()
        values.append(value if value else None)

    # Generate and execute the INSERT query
    placeholders = ", ".join(["%s"] * len(columns))
    query = f"INSERT INTO {table_name} VALUES ({placeholders})"
    try:
        cursor.execute(query, tuple(values))
        conn.commit()
        print("Record inserted successfully!")
    except Exception as e:
        print(f"Error inserting record: {e}")

def update_record(cursor, conn, table_name):
    """Update a record in the specified table."""
    # Get table schema
    cursor.execute(f"DESCRIBE {table_name}")
    columns = [row[0] for row in cursor.fetchall()]
    print(f"\nColumns in {table_name}: {', '.join(columns)}")

    # Get details for the update
    column_to_update = input("Enter the column to update: ").strip()
    if column_to_update not in columns:
        print("Invalid column name.")
        return

    new_value = input(f"Enter the new value for {column_to_update}: ").strip()
    condition = input("Enter the condition for the update (e.g., id=1): ").strip()

    # Generate and execute the UPDATE query
    query = f"UPDATE {table_name} SET {column_to_update} = %s WHERE {condition}"
    try:
        cursor.execute(query, (new_value,))
        conn.commit()
        print("Record updated successfully!")
    except Exception as e:
        print(f"Error updating record: {e}")

def delete_record(cursor, conn, table_name):
    """Delete a record from the specified table."""
    # Get deletion condition
    condition = input("Enter the condition for deletion (e.g., id=1): ").strip()

    # Generate and execute the DELETE query
    query = f"DELETE FROM {table_name} WHERE {condition}"
    try:
        cursor.execute(query)
        conn.commit()
        print("Record deleted successfully!")
    except Exception as e:
        print(f"Error deleting record: {e}")

def delete_table(cursor, conn, table_name):
    """Delete a table from the current database."""
    confirm = input(f"Are you sure you want to delete the table '{table_name}'? This action cannot be undone. (yes/no): ").strip().lower()
    if confirm == "yes":
        try:
            cursor.execute(f"DROP TABLE {table_name}")
            conn.commit()
            print(f"Table '{table_name}' has been deleted successfully!")
        except Exception as e:
            print(f"Error deleting table '{table_name}': {e}")
    else:
        print("Table deletion canceled.")


def get_table_schema(cursor, table_name):
    """
    Retrieve the list of columns and their data types from the table, 
    and divide them into categorical and numerical columns.
    
    Args:
        cursor: MySQL cursor object for executing queries.
        table_name (str): The table name.
    
    Returns:
        A dictionary with two keys: 'categorical' and 'numerical'.
    """
    try:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        # List of MySQL data types classified as categorical or numerical
        numerical_types = ['int', 'bigint', 'decimal', 'float', 'double', 'numeric']
        categorical_types = ['varchar', 'char', 'text', 'enum', 'date', 'time', 'datetime', 'year', 'tinytext', 'mediumtext', 'longtext']
        
        categorical = []
        numerical = []

        for column in columns:
            field_name = column[0]  # Column name
            data_type = column[1]  # Data type (e.g., "int(11)", "varchar(255)")
            
            base_type = data_type.split('(')[0].lower()

            if base_type in numerical_types:
                numerical.append(field_name)
            elif base_type in categorical_types:
                categorical.append(field_name)

        schema = {
            'categorical': categorical,
            'numerical': numerical
        }

        # print(f"Schema for table '{table_name}':")
        # print(f"Categorical: {categorical}")
        # print(f"Numerical: {numerical}")
        
        return schema

    except Exception as e:
        print(f"Error getting table schema: {e}")
        return {'categorical': [], 'numerical': []}