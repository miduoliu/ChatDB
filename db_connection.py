import mysql.connector
# import csv

def connect_to_db():
    """Establish a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host="localhost",          # Update with your MySQL host
            user="root",      # Update with your MySQL username
            password="",  # Update with your MySQL password
            database="",                # Leave empty; database will be selected dynamically
            allow_local_infile=True
        )
        print("Connected to MySQL database!")
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)
    # return conn
# cursor = conn.cursor()

# # data = pd.read_csv("database/olist_customers_dataset.csv")

# csv_file_path = './database/olist_customers_dataset.csv'

# with open(csv_file_path, mode='r') as csvfile:
#     reader = csv.reader(csvfile)
#     next(reader)  # Skip the header row
#     for row in reader:
#         cursor.execute("INSERT INTO your_table (column1, column2, column3, column4, column5) VALUES (%s, %s, %s, %s, %s)", row)

# conn.commit()
# cursor.close()
# conn.close()
