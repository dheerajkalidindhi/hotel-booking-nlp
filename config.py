def run_query(intent, entities=None):
    conn = psycopg2.connect(
        dbname="bookings",
        user="postgres",
        password="YOUR PASSWORD",
        host="pg-bookings",
        port="5432"
    )
