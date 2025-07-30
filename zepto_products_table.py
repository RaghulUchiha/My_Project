import psycopg2
import datetime

def create_connection():
    return psycopg2.connect(
        user="postgres",
        password="Raghul@04",
        host="127.0.0.1",
        port="5432",
        database="Players"
    )
    
def create_table():
    try:
        connection = create_connection()
        cursor = connection.cursor()
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS zepto_products (
            MRP INT,
            CHANNEL TEXT NOT NULL,
            IS_OUT_OF_STOCK TEXT NOT NULL,
            PRODUCT_ID TEXT NOT NULL
        );
        '''
            
        cursor.execute(create_table_query)
        connection.commit()
        print("Table created Successfully")
    except psycopg2.Error as error:
        print("Error creating table: ", error)
    finally:
        cursor.close()
        connection.close()