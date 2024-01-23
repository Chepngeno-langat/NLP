import mysql.connector
global cnx

cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Chepngeno_0901',
    database='pandeyji_eatery'
)

def get_order_status(order_id: int):
    # Create a cursor object
    cursor = cnx.cursor()

    # Write the SQL query
    query = ("SELECT status FROM order_tracking WHERE order_id = %s")

    # Execute the query
    cursor.execute(query, (order_id,))

    # Fetch the result
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()

    if result is not None:
        return result[0]
    else:
        return None

def get_next_order_id():
    cursor = cnx.cursor()

    query = 'SELECT MAX(order_id) FROM orders'
    cursor.execute(query)

    result = cursor.fetchone()

    cursor.close()

    if result is None:
        return 1
    else:
        return result[0] + 1

def insert_order_item(food_item, quantity, order_id):
        try:
            cursor = cnx.cursor()

            # caling the stored procedure
            cursor.callproc('insert_order_item', (food_item, quantity, order_id))

            cnx.commit()

            cursor.close()

            print("Order item inserted successfully!")

            return 1
        except mysql.connector.Error as err:
            print(f"Error inserting order item: {err}")

            # Rollback changes if necessary
            cnx.rollback()

            return -1

        except Exception as e:
            print(f"An error occurred: {e}")

            cnx.rollback()
            return -1

def delete_order(order_id):
    cursor = cnx.cursor()

    query = f"DELETE FROM order_tracking WHERE order_id={order_id};"
    cursor.execute(query)

    cursor.close()

def get_total_order_price(order_id):
    cursor = cnx.cursor()

    # Executing the SQL query to get the total order price
    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)

    # Fetching the result
    result = cursor.fetchone()[0]

    # Closing the cursor
    cursor.close()

    return result

def insert_order_tracking(order_id, status):
    cursor = cnx.cursor()

    # Inserting the record into the order_tracking table
    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))

    # Committing the changes
    cnx.commit()

    # Closing the cursor
    cursor.close()

