from db_connection import connect_to_db
from db_operation import list_databases, list_tables, show_sample_data, upload_dataset,insert_record,update_record,delete_record, delete_table, get_table_schema
from nlp_usage import preprocess_query, match_query_pattern, identify_entities, generate_sql_query_from_nl
from query_generator import generate_sql_query, generate_group_by_query,generate_sample_queries
import sys


def explore_database(cursor, conn):
    """Allow the user to explore databases, tables, and perform CRUD operations."""
    # Step 1: List Databases
    while True:
        databases = list_databases(cursor)
        print("\nAvailable Databases:")
        for i, db in enumerate(databases, 1):
            print(f"{i}. {db} - [relational]")
        print(f"{len(databases) + 1}. Back to Main Menu")
        
        db_choice = input("\nSelect a database by typing the number: ").strip()
        if db_choice == str(len(databases) + 1):
            break
        if not db_choice.isdigit() or int(db_choice) < 1 or int(db_choice) > len(databases):
            print("Invalid choice. Returning to main menu.")
            return
        
        selected_db = databases[int(db_choice) - 1]
        print(f"\nYou selected: {selected_db} database.")
        cursor.execute(f"USE {selected_db}")

        # Step 2: List Tables in the Selected Database
        while True:
            tables = list_tables(cursor, selected_db)
            print(f"\nTables in {selected_db} database:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
            
            print(f"{len(tables) + 1}. Upload Dataset")
            print(f"{len(tables) + 2}. Back to Database Selection")
            
            table_choice = input("\nSelect a table by typing the number: ").strip()
            if table_choice == str(len(tables) + 1):
                insert_table = input("\nEnter the table you want to upload: ").strip()
                upload_dataset(cursor, conn, insert_table)
                continue
            if table_choice == str(len(tables) + 2):
                break
            if not table_choice.isdigit() or int(table_choice) < 1 or int(table_choice) > len(tables):
                print("Invalid choice. Returning to main menu.")
                return
            
            selected_table = tables[int(table_choice) - 1]
            print(f"\nYou selected: {selected_table} table.")
            
            # Step 3: Perform Operations
            while True:
                print("\nAvailable Operations:")
                print("1. Show sample data")
                print("2. Insert a record")
                print("3. Update a record")
                print("4. Delete a record")
                print("5. Delete this table")
                print("6. Back to Table Selection")
                print("7. Back to Main Menu")
                
                choice = input("\nSelect an operation: ").strip()
                
                if choice == "1":
                    sample_data = show_sample_data(cursor, selected_table)
                    print("\nSample Data:")
                    print(sample_data)
                elif choice == "2":
                    insert_record(cursor, conn, selected_table)
                elif choice == "3":
                    update_record(cursor, conn, selected_table)
                elif choice == "4":
                    delete_record(cursor, conn, selected_table)
                elif choice == "5":
                    delete_table(cursor, conn, selected_table)
                    break  # Exit after table deletion
                elif choice == "6":
                    break
                elif choice == "7":
                    return
                else:
                    print("Invalid choice. Please try again.")


def sample_queries_3(cursor):
    """Generate, display, and execute sample queries dynamically based on user-selected columns."""
    # Step 1: List Databases
    databases = list_databases(cursor)
    print("\nAvailable Databases:")
    for i, db in enumerate(databases, 1):
        print(f"{i}. {db} - [relational]")
    
    db_choice = input("\nSelect a database by typing the number: ").strip()
    if not db_choice.isdigit() or int(db_choice) < 1 or int(db_choice) > len(databases):
        print("Invalid choice. Returning to main menu.")
        return
    
    selected_db = databases[int(db_choice) - 1]
    cursor.execute(f"USE {selected_db}")
    print(f"\nYou selected: {selected_db} database.")

    # Step 2: List Tables in the Selected Database
    tables = list_tables(cursor, selected_db)
    print(f"\nTables in {selected_db}:")
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    table_choice = input("\nSelect a table by typing the number: ").strip()
    if not table_choice.isdigit() or int(table_choice) < 1 or int(table_choice) > len(tables):
        print("Invalid choice. Returning to main menu.")
        return

    selected_table = tables[int(table_choice) - 1]
    print(f"\nYou selected: {selected_table} table.")

    # Step 3: Fetch Table Schema
    cursor.execute(f"DESCRIBE {selected_table}")
    columns = [desc[0] for desc in cursor.fetchall()]

    print("\nAvailable Columns:")
    for i, col in enumerate(columns, 1):
        print(f"{i}. {col}")

    # Step 4: Select Columns by Number
    try:
        group_by_index = int(input("\nSelect a column for GROUP BY (type the number): ").strip()) - 1
        where_index = int(input("Select a column for WHERE clause (type the number): ").strip()) - 1
        order_by_index = int(input("Select a column for ORDER BY (type the number): ").strip()) - 1

        # Validate indices
        if group_by_index < 0 or group_by_index >= len(columns):
            raise ValueError("Invalid column number for GROUP BY.")
        if where_index < 0 or where_index >= len(columns):
            raise ValueError("Invalid column number for WHERE.")
        if order_by_index < 0 or order_by_index >= len(columns):
            raise ValueError("Invalid column number for ORDER BY.")

        group_by_col = columns[group_by_index]
        where_col = columns[where_index]
        order_by_col = columns[order_by_index]

    except ValueError as e:
        print(f"Error: {e}. Returning to main menu.")
        return

    # Step 5: Generate Sample Queries with Descriptions
    queries = [
        {"heading": f"Group {selected_table} by {group_by_col}", "sql": f"SELECT {group_by_col}, COUNT(*) FROM {selected_table} GROUP BY {group_by_col}"},
        {"heading": f"Find {where_col} which less than 40", "sql": f"SELECT * FROM {selected_table} WHERE {where_col} < 40"},
        {"heading": f"Filter the {selected_table} by {order_by_col} in desending order", "sql": f"SELECT * FROM {selected_table} ORDER BY {order_by_col} DESC LIMIT 10"},
        {"heading": f"The number of {group_by_col} larger than 2", "sql": f"SELECT {group_by_col}, COUNT(*) FROM {selected_table} GROUP BY {group_by_col} HAVING COUNT(*) > 2"}
    ]

    # Step 6: Display Queries
    print("\nHere are some sample queries. Let me know if there is a specific type of queries you want to learn about or type 'menu'.")
    print("Enter 'execute <query_number>' to run a query.\n")
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query['heading']}\n```{query['sql']}```\n")

    # Step 7: Handle User Interaction
    while True:
        user_input = input("\nYour choice: ").strip().lower()
        if user_input == "menu":
            break
        elif user_input.startswith("execute"):
            try:
                query_number = int(user_input.split()[1])
                if query_number < 1 or query_number > len(queries):
                    print("Invalid query number. Please try again.")
                    continue
                
                # Execute the selected query
                selected_query = queries[query_number - 1]["sql"]
                print(f"\nExecuting Query:\n{selected_query}")
                cursor.execute(selected_query)
                results = cursor.fetchall()

                if results:
                    for row in results[:10]:  # Show only the first 10 rows
                        print(row)
                else:
                    print("No results returned.")
            except (IndexError, ValueError):
                print("Invalid input format. Use 'execute <query_number>'.")
            except Exception as e:
                print(f"Error executing query: {e}")
        else:
            print("Invalid input. Type 'menu' to return or 'execute <query_number>' to run a query.")

def display_sample_queries(cursor, table_name):
    """
    Display three sample queries with query descriptions and SQL results.
    
    Args:
        cursor: MySQL cursor object for executing queries.
        table_name (str): The table name.
    """
    # Step 1: Extract the table schema dynamically
    schema = get_table_schema(cursor, table_name)
    
    # Step 2: Generate the sample queries
    queries = generate_sample_queries(table_name, schema)
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query['description']}")
        print(f"SQL: {query['sql']}\n")
        
        try:
            cursor.execute(query['sql'])
            results = cursor.fetchall()
            print("Query Results (First 5 rows):")
            for row in results[:5]:  # Display only the first 5 rows
                print(row)
            print("\n" + "-" * 40 + "\n")  # Separator
        except Exception as e:
            print(f"Error executing query: {e}")

def sample_queries_2(cursor):
    """
    Generate and execute three sample queries based on specified patterns.
    """
    databases = list_databases(cursor)
    print("\nAvailable Databases:")
    for i, db in enumerate(databases, 1):
        print(f"{i}. {db} - [relational]")
    
    db_choice = input("\nSelect a database by typing the number: ").strip()
    selected_db = databases[int(db_choice) - 1]
    cursor.execute(f"USE {selected_db}")
    
    tables = list_tables(cursor, selected_db)
    print("\nTables in {selected_db}:")
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    table_choice = input("\nSelect a table by typing the number: ").strip()
    selected_table = tables[int(table_choice) - 1]
    print(f"\nYou selected: {selected_table} table.")
    
    display_sample_queries(cursor, selected_table)



def natural_language_query(cursor):
    """Process natural language queries."""
    databases = list_databases(cursor)
    print("\nAvailable Databases:")
    for i, db in enumerate(databases, 1):
        print(f"{i}. {db} - [relational]")

    db_choice = input("\nSelect a database by typing the number: ").strip()
    if not db_choice.isdigit() or int(db_choice) < 1 or int(db_choice) > len(databases):
        print("Invalid choice.")
        return

    selected_db = databases[int(db_choice) - 1]
    cursor.execute(f"USE {selected_db}")

    user_query = input("\nEnter your query in natural language: ").strip()
    tokens = preprocess_query(user_query)
    # print(f"Tokens: {tokens}")  # Debugging output

    # Step 3: Match Query Pattern
    pattern = match_query_pattern(tokens)
    if not pattern:
        print("\nCould not match your query to any known patterns.")
        return

    # Step 4: Identify Entities (table, attribute, value)
    table1, table2, attribute1, attribute2, value = identify_entities(pattern, tokens, cursor, selected_db)
    # print(f"Matched Table1: {table1}, Matched Table2: {table2}, Attribute1: {attribute1}, Attribute2: {attribute2}, Value: {value}")  # Debugging output

    if not table1 or not attribute1:
        print("Could not identify all necessary entities for query construction.")
        return

    # Step 5: Generate SQL Query
    sql_query = generate_sql_query_from_nl(pattern, table1, table2, attribute1, attribute2, value)
    if not sql_query:
        print("Failed to generate a valid SQL query.")
        return

    print(f"\nGenerated SQL Query:\n{sql_query}")

    # Step 6: Execute Query
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        print("\nQuery Results (First 5 rows):")
        for row in rows[:5]:  # Display only the first 5 rows
            print(row)
                    # Clear any remaining results
        while cursor.nextset():
            pass
    except Exception as e:
        print(f"Error executing query: {e}")


def exit_chatdb(cursor, conn):
    """Gracefully exit ChatDB."""
    print("\nExiting ChatDB... Goodbye!")
    cursor.close()
    conn.close()
    sys.exit(0)


def main():
    """Main function to run ChatDB."""
    conn = connect_to_db()
    cursor = conn.cursor()
    print("Welcome to ChatDB!")

    while True:
        print("\n----------------------")
        print("1. Explore database")
        print("2. Sample queries")
        print("3. Advanced Sample queries")
        print("4. Ask natural language query")
        print("5. Exit")
        print("----------------------")
        choice = input("\nSelect an option by typing the number: ").strip()

        if choice == "1":
            explore_database(cursor,conn)
        elif choice == "2":
            sample_queries_2(cursor)
        elif choice == "3":
            sample_queries_3(cursor)
        elif choice == "4":
            natural_language_query(cursor)
        elif choice == "5":
            exit_chatdb(cursor, conn)
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()