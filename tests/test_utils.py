from wazimap_ng.utils import sort_list_using_order

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
