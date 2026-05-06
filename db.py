import psycopg2
from config import DB_CONFIG


def run_query(intent, entities=None):

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    if entities is None:
        entities = {}

    city = entities.get("city")
    user = entities.get("user_name")
    start_date = entities.get("start_date")
    end_date = entities.get("end_date")
    keyword = entities.get("keyword")

    query = ""
    params = []

    # ================= COMMON FILTER BUILDER =================
    def apply_filters(base_query):
        conditions = []

        if city:
            conditions.append("city = %s")
            params.append(city)

        if user:
            conditions.append("user_name = %s")
            params.append(user)

        if start_date and end_date:
            conditions.append("booking_date BETWEEN %s AND %s")
            params.extend([start_date, end_date])

        if not conditions:
            return base_query

        if "WHERE" in base_query.upper():
            return base_query + " AND " + " AND ".join(conditions)
        else:
            return base_query + " WHERE " + " AND ".join(conditions)

    # ====================== INTENTS ======================

    if intent == "top_user":
        query = apply_filters("""
            SELECT user_name, COUNT(*) AS total_bookings
            FROM bookings
        """) + """
            GROUP BY user_name
            ORDER BY total_bookings DESC
            LIMIT 1;
        """

    elif intent == "top_5_users":
        query = """
            SELECT user_name, COUNT(*) AS total_bookings
            FROM bookings
            GROUP BY user_name
            ORDER BY total_bookings DESC
            LIMIT 5;
        """

    elif intent == "bookings_by_city":
        if not city:
            return {"error": "City required"}

        query = """
            SELECT *
            FROM bookings
            WHERE city = %s
            ORDER BY booking_date DESC;
        """

        params = [city]

    elif intent == "bookings_by_user":
        if not user:
            return {"error": "User required"}

        query = """
            SELECT *
            FROM bookings
            WHERE user_name = %s
            ORDER BY booking_date DESC;
        """

        params = [user]

    elif intent == "user_booking_count":
        query = """
            SELECT user_name,
                   COUNT(*) AS total_bookings,
                   MIN(booking_date) AS first_booking,
                   MAX(booking_date) AS last_booking
            FROM bookings
            GROUP BY user_name
            ORDER BY total_bookings DESC;
        """

    elif intent == "max_booking_day":
        query = """
            SELECT TO_CHAR(booking_date, 'Day') AS day_name,
                   COUNT(*) AS total
            FROM bookings
            GROUP BY day_name
            ORDER BY total DESC
            LIMIT 1;
        """

    elif intent == "min_booking_day":
        query = """
            SELECT TO_CHAR(booking_date, 'Day') AS day_name,
                   COUNT(*) AS total
            FROM bookings
            GROUP BY day_name
            ORDER BY total ASC
            LIMIT 1;
        """

    elif intent == "bookings_this_week":
        query = """
            SELECT *
            FROM bookings
            WHERE booking_date >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY booking_date DESC;
        """

    elif intent == "date_range":

        if not start_date or not end_date:
            return {"error": "Date range required"}

        query = """
            SELECT *
            FROM bookings
            WHERE booking_date BETWEEN %s AND %s
            ORDER BY booking_date DESC;
        """

        params = [start_date, end_date]

    elif intent == "satisfied_users":

        query = apply_filters("""
            SELECT *
            FROM bookings
            WHERE rating >= 4
        """) + """
            ORDER BY rating DESC;
        """

    elif intent == "complaints":

        query = apply_filters("""
            SELECT *
            FROM bookings
            WHERE rating <= 2
        """) + """
            ORDER BY rating ASC;
        """

    elif intent == "best_rated":

        query = """
            SELECT *
            FROM bookings
            ORDER BY rating DESC, booking_date DESC
            LIMIT 10;
        """

    elif intent == "worst_rated":

        query = """
            SELECT *
            FROM bookings
            ORDER BY rating ASC, booking_date DESC
            LIMIT 10;
        """

    elif intent == "best_worst_rating":

        query = """
            SELECT MAX(rating) AS best_rating,
                   MIN(rating) AS worst_rating
            FROM bookings;
        """

    elif intent == "avg_rating_city":

        query = """
            SELECT city,
                   ROUND(AVG(rating), 2) AS avg_rating,
                   COUNT(*) AS total
            FROM bookings
            GROUP BY city
            ORDER BY avg_rating DESC;
        """

    elif intent == "popular_city":

        query = """
            SELECT city,
                   COUNT(*) AS total
            FROM bookings
            GROUP BY city
            ORDER BY total DESC
            LIMIT 1;
        """

    elif intent == "hotel_performance":

        query = """
            SELECT hotel_name,
                   ROUND(AVG(rating), 2) AS avg_rating,
                   COUNT(*) AS total
            FROM bookings
            GROUP BY hotel_name
            ORDER BY avg_rating DESC;
        """

    elif intent == "avg_stay_duration":

        query = """
            SELECT ROUND(AVG(check_out_date - check_in_date), 2) AS avg_days
            FROM bookings;
        """

    elif intent == "longest_stay":

        query = """
            SELECT *,
                   (check_out_date - check_in_date) AS stay_days
            FROM bookings
            ORDER BY stay_days DESC
            LIMIT 3;
        """

    elif intent == "short_stay":

        query = """
            SELECT *,
                   (check_out_date - check_in_date) AS stay_days
            FROM bookings
            WHERE (check_out_date - check_in_date) <= 2
            ORDER BY booking_date DESC;
        """

    elif intent == "monthly_bookings":

        query = """
            SELECT TO_CHAR(booking_date, 'YYYY-MM') AS month,
                   COUNT(*) AS total
            FROM bookings
            GROUP BY month
            ORDER BY month DESC;
        """

    elif intent == "peak_booking_month":

        query = """
            SELECT TO_CHAR(booking_date, 'Month') AS month,
                   COUNT(*) AS total
            FROM bookings
            GROUP BY month
            ORDER BY total DESC
            LIMIT 1;
        """

    elif intent == "search_review":

        if not keyword:
            return {"error": "Keyword required"}

        query = """
            SELECT *
            FROM bookings
            WHERE review_text ILIKE %s
            ORDER BY booking_date DESC;
        """

        params = [f"%{keyword}%"]

    elif intent == "total_bookings":

        query = """
            SELECT COUNT(*) AS total_bookings
            FROM bookings;
        """

    elif intent == "rating_distribution":

        query = """
            SELECT rating,
                   COUNT(*) AS count
            FROM bookings
            GROUP BY rating
            ORDER BY rating DESC;
        """

    elif intent == "upcoming_checkins":

        query = """
            SELECT *
            FROM bookings
            WHERE check_in_date >= CURRENT_DATE
            ORDER BY check_in_date ASC;
        """

    elif intent == "status_summary":

        query = """
            SELECT status,
                   COUNT(*) AS total
            FROM bookings
            GROUP BY status;
        """

    else:
        return {"error": "Unknown intent"}

    # ================= EXECUTION =================

    try:
        cursor.execute(query, params)

        rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]

        result = [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        result = {"error": str(e)}

    finally:
        cursor.close()
        conn.close()

    return result