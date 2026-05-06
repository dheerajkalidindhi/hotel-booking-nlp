QUERY_MAP = {
    "top_user": """
        SELECT user_name, COUNT(*) as total_bookings
        FROM bookings
        GROUP BY user_name
        ORDER BY total_bookings DESC
        LIMIT 1;
    """,

    "max_booking_day": """
        SELECT TO_CHAR(booking_date, 'Day') AS day, COUNT(*) as total
        FROM bookings
        GROUP BY day
        ORDER BY total DESC
        LIMIT 1;
    """,

    "min_booking_day": """
        SELECT TO_CHAR(booking_date, 'Day') AS day, COUNT(*) as total
        FROM bookings
        GROUP BY day
        ORDER BY total ASC
        LIMIT 1;
    """,

    "bookings_this_week": """
        SELECT *
        FROM bookings
        WHERE booking_date BETWEEN '2026-04-01' AND '2026-04-07';
    """,

    "satisfied_users":  """
        SELECT DISTINCT user_name
        FROM bookings
        WHERE rating >= 4;
    """,

    "best_worst_rating": """
        SELECT MAX(rating) as best_rating, MIN(rating) as worst_rating
        FROM bookings;
    """,

    "complaints": """
        SELECT user_name, review_text
        FROM bookings
        WHERE rating <= 2;
    """,

    "bookings_by_city": """
       SELECT *
       FROM bookings
       WHERE city = '{city}';
    """,

}

