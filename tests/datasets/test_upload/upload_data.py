dataset_upload_data = {
    "accurate": {
        "rows": [
            ["Geography","Age","Race","Gender","Income","Count"],
            ["ZA","05 - 09","Black African","Female","No income","181"],
            ["ZA","05 - 09","Black African","Male","No income","278"],
            ["ZA","05 - 09","Black African","Female","No income","7"],
            ["ZA","05 - 09","Black African","Male","No income","58"]
        ],
    },
    "extra_white_spaces": {
        "rows":[
            ["Geography ","Age ","Race","  Gender","Income","Count "],
            ["ZA"," 05 - 09","Black African","Female ","No income ","181"],
            ["ZA ","05 - 09","Black African ","Male","No income","278"],
            ["ZA","05 - 09","Black African","Female"," No income","7"],
            ["ZA","05 - 09","Black African","  Male","No income","58"]
        ],
    },

    "Mixed_casing_test": {
        "rows":[
            ["GeogrAPHY","AGE","RAce","GEndeR","InCOME","CounT"],
            ["ZA","05 - 09","Black African","FemaLe","No inCome","181"],
            ["ZA","05 - 09","Black African","Male","No INCOME","278"],
            ["ZA","05 - 09","BLACK African","Female","No income","7"],
            ["za","05 - 09","Black African","MALE","No income","58"]
        ],
    },

    "empty_col": {
        "rows":[
            ["","","Geography","Age","Race","","Gender","Income","Count",""],
            ["","","ZA","05 - 09","Black African","","Female","No income","181",""],
            ["","","ZA","05 - 09","Black African","","Male","No income","278",""],
            ["","","ZA","05 - 09","Black African","","Female","No income","7",""],
            ["","","ZA","05 - 09","Black African","","Male","No income","58",""]
        ],
    },

    "empty_rows": {
        "rows":[
            ["Geography","Age","Race","Gender","Income","Count"],
            ["ZA","05 - 09","Black African","Female","No income","181"],
            ["","","","","",""],
            ["ZA","05 - 09","Black African","Male","No income","278"],
            ["ZA","05 - 09","Black African","Female","No income","7"],
            ["ZA","05 - 09","Black African","Male","No income","58"],
            ["","","","","",""],
        ],
    },
    "empty_cols_for_header": {
        "rows":[
            ["Geography","Age","Race","Gender","Income","Count", "Test"],
            ["ZA","05 - 09","Black African","Female","No income","181", ""],
            ["ZA","05 - 09","Black African","Male","No income","278", ""],
            ["ZA","05 - 09","Black African","Female","No income","7", ""],
            ["ZA","05 - 09","Black African","Male","No income","58", ""],
        ],
        "results":[
            {'age': '05 - 09', 'race': 'Black african', 'count': '181', 'gender': 'Female', 'income': 'No income', 'test': ''},
            {'age': '05 - 09', 'race': 'Black african', 'count': '278', 'gender': 'Male', 'income': 'No income', 'test': ''},
            {'age': '05 - 09', 'race': 'Black african', 'count': '7', 'gender': 'Female', 'income': 'No income', 'test': ''},
            {'age': '05 - 09', 'race': 'Black african', 'count': '58', 'gender': 'Male', 'income': 'No income', 'test': ''}
        ]
    }
}

default_result_set = [
    {'age': '05 - 09', 'race': 'Black african', 'count': '181', 'gender': 'Female', 'income': 'No income'},
    {'age': '05 - 09', 'race': 'Black african', 'count': '278', 'gender': 'Male', 'income': 'No income'},
    {'age': '05 - 09', 'race': 'Black african', 'count': '7', 'gender': 'Female', 'income': 'No income'},
    {'age': '05 - 09', 'race': 'Black african', 'count': '58', 'gender': 'Male', 'income': 'No income'}
]
