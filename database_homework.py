import psycopg2

def get_connection():
    conn = psycopg2.connect(
        dbname="homework",
        user="brlz", 
        password="your_password",
        host="localhost",
        port="5432"
    )
    return conn

def init_db(conn):
    with conn.cursor() as cur:
        print("этап 1: возводим фундамент для таблиц...")
        cur.execute("CREATE TYPE transport_type AS ENUM ('bus', 'train', 'plane');")
        cur.execute("""
            CREATE TABLE passengers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                passport_number VARCHAR(20) UNIQUE
            );
        """)
        cur.execute("""
            CREATE TABLE transport (
                id SERIAL PRIMARY KEY,
                type transport_type,
                model_or_route VARCHAR(100),
                capacity INT
            );
        """)
        cur.execute("""
            CREATE TABLE bookings (
                id SERIAL PRIMARY KEY,
                passenger_id INT REFERENCES passengers(id),
                transport_id INT REFERENCES transport(id),
                seat_number INT,
                booking_date DATE
            );
        """)
        print("фундамент залит! таблицы готовы к работе.")

        print("\nэтап 2: заселяем таблицы свежими данными...")
        passengers_to_add = [
            ('Иван Петров', 'AA123456'), ('Мария Сидорова', 'BB789012'), ('Алексей Иванов', 'CC345678')
        ]
        for p in passengers_to_add:
            cur.execute("INSERT INTO passengers (name, passport_number) VALUES (%s, %s)", p)

        transport_to_add = [
            ('bus', 'Маршрут 101', 40), ('train', 'Поезд "Стриж"', 200), ('plane', 'Boeing 737', 150)
        ]
        for t in transport_to_add:
            cur.execute("INSERT INTO transport (type, model_or_route, capacity) VALUES (%s, %s, %s)", t)

        bookings_to_add = [
            (1, 1, 10, '2025-05-15'), (1, 2, 55, '2025-06-20'), (1, 3, 1, '2025-07-01'),
            (2, 1, 12, '2025-05-18'), (2, 2, 60, '2025-05-25'), (3, 3, 18, '2024-12-10')
        ]
        for b in bookings_to_add:
            cur.execute("INSERT INTO bookings (passenger_id, transport_id, seat_number, booking_date) VALUES (%s, %s, %s, %s)", b)

        print("все на месте! данные успешно загружены.")
        conn.commit()

def run_queries(conn):
    with conn.cursor() as cur:
        print("\n--- часть 3: магия sql-запросов и аналитики ---")

        cur.execute("SELECT DISTINCT p.name FROM passengers p JOIN bookings b ON p.id = b.passenger_id;")
        print("\nа) вот список наших путешественников (с бронями):", [row[0] for row in cur.fetchall()])

        cur.execute("SELECT t.model_or_route, COUNT(b.id) FROM transport t LEFT JOIN bookings b ON t.id = b.transport_id GROUP BY t.id;")
        print("\nб) сколько мест уже занято в каждом транспорте:")
        for row in cur.fetchall():
            print(f"  - в '{row[0]}' занято: {row[1]} кресел")

        cur.execute("SELECT p.name FROM passengers p JOIN bookings b ON p.id = b.passenger_id WHERE b.booking_date >= '2025-05-01' AND b.booking_date < '2025-06-01';")
        print("\nв) майские жуки! пассажиры, летящие в мае 2025:", [row[0] for row in cur.fetchall()])

        cur.execute("SELECT t.model_or_route FROM transport t JOIN bookings b ON t.id = b.transport_id GROUP BY t.id ORDER BY COUNT(b.id) DESC LIMIT 1;")
        print("\nг) и барабанная дробь... самый популярный транспорт:", cur.fetchone())

        transport_id = 1
        cur.execute("SELECT seat_number FROM bookings WHERE transport_id = %s", (transport_id,))
        booked_seats = {row[0] for row in cur.fetchall()}
        all_seats = set(range(1, 41))
        free_seats = sorted(list(all_seats - booked_seats))
        print(f"\nд) хочешь в автобус (id={transport_id})? свободные места:", free_seats)

        print("\n--- часть 4: акробатика с join'ами и подзапросами ---")
        
        cur.execute("SELECT p.name, p.passport_number, t.type, b.seat_number FROM passengers p JOIN bookings b ON p.id = b.passenger_id JOIN transport t ON b.transport_id = t.id;")
        print("\nа) полный расклад по всем бронированиям:")
        for row in cur.fetchall():
            print(f"  - кто: {row[0]} (паспорт {row[1]}), куда: {row[2]}, место: {row[3]}")

        cur.execute("SELECT p.name FROM passengers p JOIN bookings b ON p.id = b.passenger_id JOIN transport t ON b.transport_id = t.id GROUP BY p.id HAVING COUNT(DISTINCT t.type) > 1;")
        print("\nв) настоящие ценители! пассажиры-универсалы:", [row[0] for row in cur.fetchall()])

def manage_indexes(conn):
    with conn.cursor() as cur:
        print("\n--- часть 5: немного магии для ускорения ---")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_booking_date ON bookings(booking_date);")
        conn.commit()
        print("индекс для booking_date создан! теперь поиск по датам будет летать.")

if __name__ == "__main__":
    conn = None
    try:
        conn = get_connection()
        init_db(conn)
        print(">>> погнали выполнять запросы! <<<")
        run_queries(conn)
        manage_indexes(conn)
    except psycopg2.Error as e:
        print(f"ой, всё! что-то пошло не так с базой данных.")
        print(e)
    finally:
        if conn:
            conn.close()
            print("\nмиссия выполнена. отключаюсь от базы.") 