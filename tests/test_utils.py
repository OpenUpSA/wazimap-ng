import codecs
import csv
from io import BytesIO

from wazimap_ng.utils import detect_encoding, sort_list_using_order


def test_empty_sort_using_order():
    lst = []
    order = []

    sorted_lst = sort_list_using_order(lst, order)
    assert sorted_lst == []

def test_sort_using_order_with_empty_order():
    lst = [2, 3, 1]
    order = []
    sorted_lst = sort_list_using_order(lst, order)
    assert sorted_lst == lst

def test_sort_using_order_with_none_order():
    lst = [2, 3, 1]
    sorted_lst = sort_list_using_order(lst, None)
    assert sorted_lst == lst

def test_sort_using_order_with_complete_order():
    lst = ["a", "b", "c"]
    order = ["b", "c", "a"]
    sorted_lst = sort_list_using_order(lst, order)
    assert sorted_lst == order

def test_sort_using_order_with_missing_values():
    lst = ["a", "b", "c"]
    order = ["b", "a"]
    sorted_lst = sort_list_using_order(lst, order)
    assert sorted_lst == ["b", "a", "c"]

def test_sort_using_order_with_custom_key():
    lst = [(1, "a"), (2, "b"), (3, "c")]
    order = ["b", "a", "c"]
    sorted_lst = sort_list_using_order(lst, order, key_func=lambda x: x[1])
    assert sorted_lst == [(2, "b"), (1, "a"), (3, "c")]


def generate_file(data, header, encoding="utf8"):
    buffer = BytesIO()
    StreamWriter = codecs.getwriter(encoding)
    text_buffer = StreamWriter(buffer)

    writer = csv.writer(text_buffer)
    writer.writerow(header)
    writer.writerows(data)

    buffer.seek(0)
    return buffer


data_with_different_encodings = [
    ("GEOCODE_1", "‘F1_value_1", "F2_value_1’", 111),
    ("GEOCODE_2", "€ŠF1_value_2", "F2_value_2®®", 222),
]
good_header = ["Geography", "field1", "field2", "count"]


def test_detect_encoding():
    buffer = generate_file(data_with_different_encodings, good_header, "Windows-1252")
    encoding = detect_encoding(buffer)
    assert encoding == "Windows-1252"
