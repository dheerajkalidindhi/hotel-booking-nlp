def run_query(intent, entities=None):
    conn = psycopg2.connect(
        dbname="bookings",
        user="postgres",
        password="1234",
        host="pg-bookings",
        port="5432"
    )