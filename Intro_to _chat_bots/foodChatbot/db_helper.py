import mysql.connector
global cnx

cnx = mysql.connector.connect(
    host='localhost',
    user='root',
    password='chepngeno',
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
    cnx.close()

    if result is not None:
        return result[0]
    else:
        return None