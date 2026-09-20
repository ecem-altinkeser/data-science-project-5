import datetime
from decimal import Decimal
import sys
import os
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from data.question import (
    clean_null_emails,
    find_invalid_emails,
    get_first_3_letters_of_names,
    get_email_domains,
    concat_name_and_email,
    cast_total_amount_to_integer,
    find_at_position_in_email,
    fill_null_product_category,
    rank_customers_by_spending,
    running_total_per_customer,
    get_electronics_and_appliances,
    get_orders_with_missing_customers,
)


# Q1: NULL emailleri 'unknown@example.com' ile değiştir (UPDATE)
def test_clean_null_emails():
    assert clean_null_emails() is None


# Q2: @ işareti geçmeyen emailleri bul
def test_find_invalid_emails():
    result = find_invalid_emails()
    assert isinstance(result, list)
    assert len(result) >= 1
    # Sonuçlarda 'denizyildiz.com' olmalı (@ yok)
    all_values = [str(col) for r in result for col in r]
    assert any('denizyildiz.com' in v for v in all_values)


# Q3: İsimlerin ilk 3 harfi (full_name, short_name)
def test_get_first_3_letters_of_names():
    result = get_first_3_letters_of_names()
    assert isinstance(result, list)
    names = {r[0]: r[1] for r in result}
    assert names['Ali Veli'] == 'Ali'
    assert names['Ayşe Yılmaz'] == 'Ayş'
    assert names['Mehmet Can'] == 'Meh'


# Q4: Email domain (full_name, domain)
def test_get_email_domains():
    result = get_email_domains()
    assert isinstance(result, list)
    domains = {r[0]: r[1] for r in result}
    assert domains['Ali Veli'] == 'example.com'
    assert domains['Ayşe Yılmaz'] == 'example.com'


# Q5: İsim + email birleştir (full_info: 'isim - email')
def test_concat_name_and_email():
    result = concat_name_and_email()
    assert isinstance(result, list)
    infos = [r[0] for r in result]
    assert 'Ali Veli - ali@example.com' in infos


# Q6: total_amount INTEGER'a çevir (order_id, total_amount_int)
def test_cast_total_amount_to_integer():
    result = cast_total_amount_to_integer()
    assert isinstance(result, list)
    amounts = {r[0]: r[1] for r in result}
    assert amounts[1] == 500
    assert amounts[2] == 150
    assert amounts[3] == 300
    assert all(isinstance(r[1], int) for r in result)


# Q7: @ işaretinin indeks pozisyonu (full_name, at_position)
def test_find_at_position_in_email():
    result = find_at_position_in_email()
    assert isinstance(result, list)
    positions = {r[0]: r[1] for r in result}
    # POSITION('@' IN 'ali@example.com') = 4
    assert positions['Ali Veli'] == 4
    assert isinstance(positions['Ali Veli'], int)


# Q8: NULL kategorileri 'Unknown' ile değiştir (product_name, product_category)
def test_fill_null_product_category():
    result = fill_null_product_category()
    assert isinstance(result, list)
    categories = {r[0]: r[1] for r in result}
    assert categories['Laptop'] == 'Electronics'
    assert categories['Mouse'] == 'Unknown'
    assert all(v is not None and v != '' for v in categories.values())


# Q9: Harcamaya göre RANK (customer_id, total_amount, rank_by_spend)
def test_rank_customers_by_spending():
    result = rank_customers_by_spending()
    assert isinstance(result, list)
    assert len(result) == 3
    # En yüksek harcama: customer 1 (500), sonra 3 (300), sonra 2 (150)
    assert result[0][2] == 1  # rank 1
    assert result[0][1] == Decimal('500.00')


# Q10: Running total (order_id, customer_id, total_amount, running_total)
def test_running_total_per_customer():
    result = running_total_per_customer()
    assert isinstance(result, list)
    assert len(result) == 3
    for r in result:
        assert len(r) == 4
        assert r[3] >= r[2]  # running_total >= total_amount


# Q11: Electronics + Appliances ürünleri (product_name, category)
def test_get_electronics_and_appliances():
    result = get_electronics_and_appliances()
    assert isinstance(result, list)
    names = [r[0] for r in result]
    assert 'Laptop' in names
    assert 'Tablet' in names
    assert 'Buzdolabı' in names
    assert 'Mouse' not in names  # Mouse'un kategorisi NULL
    for r in result:
        assert r[1] in ('Electronics', 'Appliances')


# Q12: Tüm siparişler + siparişi olmayan müşteriler
def test_get_orders_with_missing_customers():
    result = get_orders_with_missing_customers()
    assert isinstance(result, list)
    assert len(result) >= 3


def send_post_request(url: str, data: dict, headers: dict = None):
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
    except Exception as err:
        print(f"Other error occurred: {err}")


class ResultCollector:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            if report.passed:
                self.passed += 1
            elif report.failed:
                self.failed += 1


def run_tests():
    collector = ResultCollector()
    pytest.main(["tests"], plugins=[collector])
    total = collector.passed + collector.failed
    print(f"\nToplam Başarılı: {collector.passed}")
    print(f"Toplam Başarısız: {collector.failed}")

    if total == 0:
        print("Hiç test çalıştırılmadı.")
        return

    user_score = round((collector.passed / total) * 100, 2)
    print(f"Skor: {user_score}")

    url = "https://kaizu-api-8cd10af40cb3.herokuapp.com/projectLog"
    payload = {
        "user_id": 830,
        "project_id": 38,
        "user_score": user_score,
        "is_auto": False
    }
    headers = {"Content-Type": "application/json"}
    send_post_request(url, payload, headers)


if __name__ == "__main__":
    run_tests()
