# **ChatDB**

## **Table of Contents**
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Setup and Installation](#setup-and-installation)
4. [How to Run the Program](#how-to-run-the-program)
5. [Main Menu Options](#main-menu-options)
6. [File Descriptions](#file-descriptions)


---

## **Introduction**
**ChatDB** is an interactive command-line tool that allows users to query and manipulate relational databases using **natural language**. It bridges the gap between everyday language and SQL syntax, enabling non-technical users to extract and manipulate data with ease.

**Key Features:**
- **Natural Language Querying**: Query the database using simple natural language commands.
- **SQL Query Generation**: Supports **WHERE**, **ORDER BY**, **GROUP BY**, **HAVING**, **GROUP BY-HAVING**clauses.
- **CRUD Operations**: Easily create, read, update, and delete records in the database.
- **Interactive Menu**: Simple CLI-based interface for users to navigate the system.
- **Dynamic Attribute Recognition**: Automatically detects and categorizes table attributes into categorical and numerical attributes.

---

## **Project Structure**
# File Structure
ChatDB/ ├── db_connection.py # Handles MySQL database connection ├── db_operation.py # Contains CRUD operations and utility functions ├── query_generator.py # Generates SQL queries for different operations ├── nlp_usage.py # Handles natural language processing and query generation ├── main.py # Main entry point for the ChatDB CLI application └── README.md # Project documentation

---


## **Setup and Installation**
To set up the ChatDB project on your local machine, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/miduoliu/ChatDB.git
   cd ChatDB

2. **Install the required libraries**
   ```bash
   pip install -r requirements.txt
   
3. **Set up your MySQL database and update the connection credentials in db_connection.py**

---

## **How to Run the Program**

1. **Navigate to the project directory**

2. **Run the main.py file**
   ```bash
   python main.py

3. **Follow the interactive menu to explore the database, execute queries, and more.**
---


## **Main Menu Options**

1. **Explore Database:** Browse databases, view tables, and perform CRUD operations
2. **Sample Queries:** View and execute pre-generated sample SQL queries.
3. **Advanced Sample Queries:** Dynamically generate and execute queries based on selected table attributes.
4. **Ask Natural Language Query:** Enter a query in natural language, and ChatDB will generate and execute the equivalent SQL query.
5. **Exit:** Exit the program gracefully.

---


## **File Descriptions**

## **1. db_connection.py**
**Purpose:** Establishes a connection to the MySQL database.

---

## **2. db_operation.py**
**Purpose:** Contains utility functions for interacting with the database, such as CRUD operations, listing databases/tables, showing sample data and delete tables.

---

## **3. main.py**
**Purpose:** The main entry point of ChatDB. It provides a command-line interface (CLI) for users to explore databases, run CRUD operations, generate sample queries, and interact using natural language.

### **Query Patterns in Example Query:**
1. **WHERE**
2. **MIN, MAX**  
3. **ORDER BY**
4. **limit**
5. **SUM, COUNT**
7. **GROUP BY**

---

## **4. nlp_usage.py**
**Purpose:** Handles Natural Language Processing (NLP) to process and convert user queries into SQL queries.

### **Query Patterns in Natual language:**
1. **WHERE**:  
   e.g., "Find all orders where customer_id is 123".
2. **MIN, MAX**:  
   e.g., "Let me know the maximum payment value".
3. **ORDER BY**:  
   e.g., "List all customers ordered by last purchase".
4. **JOIN**:  
   e.g., "Combine customer data with orders data".
5. **SUM, COUNT**
   e.g., "How many records of customers state in my dataset".

---

## **5. query_generator.py**
**Purpose:** Generates SQL queries for sample queries, supporting different SQL clauses like GROUP BY, WHERE, and INNER JOIN.

---











