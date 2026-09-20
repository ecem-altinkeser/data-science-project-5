import psycopg2

## Bu değeri localinde çalışırken kendi passwordün yap. Ama kodu pushlarken 'postgres' olarak bırak.
password = 'postgres'

def connect_db():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password=password
    )

# 1- Null emailleri 'unknown@example.com' ile değiştir
def clean_null_emails():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""UPDATE dsdata5.customers
                            SET email='unknown@example.com'
                            WHERE email is null;
                            """)
            conn.commit()

# 2- Hatalı emailleri bul
def find_invalid_emails():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT*
                            FROM dsdata5.customers
                            WHERE email not ILIKE'%@%';""")
            return cur.fetchall()

# 3- İsimlerin ilk 3 harfi
def get_first_3_letters_of_names():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT full_name, LEFT(full_name, 3) as short_name
                            FROM dsdata5.customers;""")
            return cur.fetchall()

# 4- Email domainlerini bul
def get_email_domains():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT full_name, 
                            CASE
                                WHEN email ILIKE'%@%' THEN SUBSTR(email, strpos(email,'@')+1) 
                                ELSE ''
                            END as "domain"
                            FROM dsdata5.customers;""")
            return cur.fetchall()

# 5- İsim ve email birleştir
def concat_name_and_email():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT concat(full_name, ' - ', email) as "full_info"
                            FROM dsdata5.customers;
                            """)
            return cur.fetchall()

# 6- Sipariş tutarlarını tam sayıya çevir
def cast_total_amount_to_integer():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT order_id, Cast(total_amount as integer) as total_amount_int
                            FROM dsdata5.orders;
                            """)
            return cur.fetchall()

# 7- Email '@' pozisyonu
def find_at_position_in_email():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT full_name, strpos(email,'@') as "at_position"
                            FROM dsdata5.customers;""")
            return cur.fetchall()

# 8- NULL kategoriye 'Unknown' yaz
def fill_null_product_category():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT product_name,
                            case
                                WHEN category ISNULL Then 'Unknown'
                                ELSE category
                            End As product_category
                            FROM dsdata5.products;
                            """)
            return cur.fetchall()

# 9- Müşteri harcama sıralaması (RANK)
def rank_customers_by_spending():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT customer_id, total_amount,
                            Rank()over (order by total_amount desc) as rank_by_spend
                            FROM dsdata5.orders;

                            """)
            return cur.fetchall()

# 10- Müşteri siparişlerinde running total
def running_total_per_customer():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT order_id, customer_id, total_amount,
                            sum(total_amount) over(
                                order by order_id
                            )as running_total
                        FROM dsdata5.orders;""")
            return cur.fetchall()

# 11- Elektronik ve Beyaz Eşya ürünleri (UNION)
def get_electronics_and_appliances():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT product_name, category
                        FROM dsdata5.products
                        Where category in ('Electronics', 'Appliances');""")
            return cur.fetchall()

# 12- Tüm siparişler ve eksik siparişler (UNION ALL)
def get_orders_with_missing_customers():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT*
                            FROM dsdata5.orders as o
                            RIGHT Join dsdata5.customers as c
                            on c.customer_id = o.customer_id;
                            """)
            return cur.fetchall()