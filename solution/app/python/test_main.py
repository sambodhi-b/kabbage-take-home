import datetime as dt
import json

import pytest

from main import raw_data_to_feature_tuple, _get_date_only


def test_raw_data_to_feature_tuple_with_great_data():

    date_pre_30 = (_get_date_only() -
                   dt.timedelta(days=33)).strftime("%Y-%m-%d")
    date_1_post_30 = (_get_date_only() -
                      dt.timedelta(days=28)).strftime("%Y-%m-%d")
    date_2_post_30 = (_get_date_only() -
                      dt.timedelta(days=3)).strftime("%Y-%m-%d")

    input_json = {
        "UserID":  "256367de-d0b1-4864-90c8-2be1ff81b33f",
        "CurrentBalance":  9270.02,
        "FICOScore": 476,
        "Transactions": [
            {"TransactionID": "edaaebb5-40a1-40e5-b286-86efe90b5336",
             "Amount":        123.45,
             "Category":      "Entertainment",
             "Type":          "debit",
             "PostDate":      date_pre_30
             },
            {"TransactionID": "9ABCDEF0-1234-5678-9ABCDEF012345",
             "Amount":        2048.64,
             "Category":      "Deposits",
             "Type":          "credit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-5678-9ABCDEF012345",
             "Amount":        121.11,
             "Category":      "Deposits",
             "Type":          "credit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-78AB-9ABCDEF012345",
             "Amount":        127.34,
             "Category":      "XXX-44",
             "Type":          "debit",
             "PostDate":      date_2_post_30
             }
        ]
    }

    assert (
        raw_data_to_feature_tuple(input_json) ==
        {'current_balance': 9270.02, 'fico_score': 476,
         'max_bal_l30': 9397.36, 'min_bal_l30': 7227.61,
         'sum_credit_l30': 2169.75, 'sum_debit_l30': 127.34,
         'catg_max_debits': 'XXX-44'})


def test_raw_data_to_feature_tuple_with_no_current_balance():

    date_pre_30 = (dt.datetime.today() -
                   dt.timedelta(days=33)).strftime("%Y-%m-%d")
    date_1_post_30 = (dt.datetime.today() -
                      dt.timedelta(days=28)).strftime("%Y-%m-%d")
    date_2_post_30 = (dt.datetime.today() -
                      dt.timedelta(days=3)).strftime("%Y-%m-%d")

    input_json = {
        "UserID":  "256367de-d0b1-4864-90c8-2be1ff81b33f",
        "CurrentBalance":  9270.02,
        "Transactions": [
            {"TransactionID": "edaaebb5-40a1-40e5-b286-86efe90b5336",
             "Amount":        123.45,
             "Category":      "Entertainment",
             "Type":          "debit",
             "PostDate":      date_pre_30
             },
            {"TransactionID": "9ABCDEF0-1234-5678-9ABCDEF012345",
             "Amount":        2048.64,
             "Category":      "Deposits",
             "Type":          "credit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-5678-9ABCDEF012345",
             "Amount":        121.11,
             "Category":      "Deposits",
             "Type":          "credit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-78AB-9ABCDEF012345",
             "Amount":        127.34,
             "Category":      "XXX-44",
             "Type":          "debit",
             "PostDate":      date_2_post_30
             }
        ]
    }


def test_raw_data_to_feature_tuple_with_no_fico_score():

    date_pre_30 = (dt.datetime.today() -
                   dt.timedelta(days=33)).strftime("%Y-%m-%d")
    date_1_post_30 = (dt.datetime.today() -
                      dt.timedelta(days=28)).strftime("%Y-%m-%d")
    date_2_post_30 = (dt.datetime.today() -
                      dt.timedelta(days=3)).strftime("%Y-%m-%d")

    input_json = {
        "UserID":  "256367de-d0b1-4864-90c8-2be1ff81b33f",
        "FICOScore": 476,
        "Transactions": [
            {"TransactionID": "edaaebb5-40a1-40e5-b286-86efe90b5336",
             "Amount":        123.45,
             "Category":      "Entertainment",
             "Type":          "debit",
             "PostDate":      date_pre_30
             },
            {"TransactionID": "9ABCDEF0-1234-5678-9ABCDEF012345",
             "Amount":        2048.64,
             "Category":      "Deposits",
             "Type":          "credit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-5678-9ABCDEF012345",
             "Amount":        121.11,
             "Category":      "Deposits",
             "Type":          "credit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-78AB-9ABCDEF012345",
             "Amount":        127.34,
             "Category":      "XXX-44",
             "Type":          "debit",
             "PostDate":      date_2_post_30
             }
        ]
    }

    with pytest.raises(KeyError) as e:
        raw_data_to_feature_tuple(input_json)


def test_raw_data_to_feature_tuple_with_no_transactions():

    input_json = {
        "UserID":  "256367de-d0b1-4864-90c8-2be1ff81b33f",
        "CurrentBalance":  9270.02,
        "FICOScore": 476,
        "Transactions": [
        ]
    }

    assert (
        raw_data_to_feature_tuple(input_json) ==
        {'current_balance': 9270.02, 'fico_score': 476,
         'max_bal_l30': 9270.02, 'min_bal_l30': 9270.02,
         'sum_credit_l30': 0, 'sum_debit_l30': 0,
         'catg_max_debits': 'None'})


def test_raw_data_to_feature_tuple_with_no_transactions_in_last_30_days():

    date_pre_30 = (dt.datetime.today() -
                   dt.timedelta(days=33)).strftime("%Y-%m-%d")
    date_1_post_30 = (dt.datetime.today() -
                      dt.timedelta(days=35)).strftime("%Y-%m-%d")
    date_2_post_30 = (dt.datetime.today() -
                      dt.timedelta(days=43)).strftime("%Y-%m-%d")

    input_json = {
        "UserID":  "256367de-d0b1-4864-90c8-2be1ff81b33f",
        "CurrentBalance":  9270.02,
        "FICOScore": 476,
        "Transactions": [
            {"TransactionID": "edaaebb5-40a1-40e5-b286-86efe90b5336",
             "Amount":        123.45,
             "Category":      "Entertainment",
             "Type":          "debit",
             "PostDate":      date_pre_30
             },
            {"TransactionID": "9ABCDEF0-1234-5678-9ABCDEF012345",
             "Amount":        2048.64,
             "Category":      "Deposits",
             "Type":          "credit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-5678-9ABCDEF012345",
             "Amount":        121.11,
             "Category":      "Deposits",
             "Type":          "credit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-78AB-9ABCDEF012345",
             "Amount":        127.34,
             "Category":      "XXX-44",
             "Type":          "debit",
             "PostDate":      date_2_post_30
             }
        ]
    }

    assert (
        raw_data_to_feature_tuple(input_json) ==
        {'current_balance': 9270.02, 'fico_score': 476,
         'max_bal_l30': 9270.02, 'min_bal_l30': 9270.02,
         'sum_credit_l30': 0, 'sum_debit_l30': 0,
         'catg_max_debits': 'XXX-44'})


def test_raw_data_to_feature_tuple_with_no_debits_in_last_30_days():

    date_pre_30 = (dt.datetime.today() -
                   dt.timedelta(days=33)).strftime("%Y-%m-%d")
    date_1_post_30 = (dt.datetime.today() -
                      dt.timedelta(days=28)).strftime("%Y-%m-%d")
    date_2_post_30 = (dt.datetime.today() -
                      dt.timedelta(days=3)).strftime("%Y-%m-%d")

    input_json = {
        "UserID":  "256367de-d0b1-4864-90c8-2be1ff81b33f",
        "CurrentBalance":  9270.02,
        "FICOScore": 476,
        "Transactions": [
            {"TransactionID": "edaaebb5-40a1-40e5-b286-86efe90b5336",
             "Amount":        123.45,
             "Category":      "Entertainment",
             "Type":          "credit",
             "PostDate":      date_pre_30
             },
            {"TransactionID": "9ABCDEF0-1234-5678-9ABCDEF012345",
             "Amount":        2048.64,
             "Category":      "Deposits",
             "Type":          "credit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-5678-9ABCDEF012345",
             "Amount":        121.11,
             "Category":      "Deposits",
             "Type":          "credit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-78AB-9ABCDEF012345",
             "Amount":        127.34,
             "Category":      "XXX-44",
             "Type":          "credit",
             "PostDate":      date_2_post_30
             }
        ]
    }

    assert (
        raw_data_to_feature_tuple(input_json) ==
        {'current_balance': 9270.02, 'fico_score': 476,
         'max_bal_l30': 9270.02, 'min_bal_l30': 6972.93,
         'sum_credit_l30': 2297.09, 'sum_debit_l30': 0,
         'catg_max_debits': 'None'})


def test_raw_data_to_feature_tuple_with_no_credits_in_last_30_days():

    date_pre_30 = (dt.datetime.today() -
                   dt.timedelta(days=33)).strftime("%Y-%m-%d")
    date_1_post_30 = (dt.datetime.today() -
                      dt.timedelta(days=28)).strftime("%Y-%m-%d")
    date_2_post_30 = (dt.datetime.today() -
                      dt.timedelta(days=3)).strftime("%Y-%m-%d")

    input_json = {
        "UserID":  "256367de-d0b1-4864-90c8-2be1ff81b33f",
        "CurrentBalance":  9270.02,
        "FICOScore": 476,
        "Transactions": [
            {"TransactionID": "edaaebb5-40a1-40e5-b286-86efe90b5336",
             "Amount":        123.45,
             "Category":      "Entertainment",
             "Type":          "debit",
             "PostDate":      date_pre_30
             },
            {"TransactionID": "9ABCDEF0-1234-5678-9ABCDEF012345",
             "Amount":        2048.64,
             "Category":      "XXX-33",
             "Type":          "debit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-5678-9ABCDEF012345",
             "Amount":        121.11,
             "Category":      "Deposits",
             "Type":          "debit",
             "PostDate":      date_1_post_30
             },
            {"TransactionID": "ABCDEF12-1234-78AB-9ABCDEF012345",
             "Amount":        127.34,
             "Category":      "XXX-44",
             "Type":          "debit",
             "PostDate":      date_2_post_30
             }
        ]
    }

    assert (
        raw_data_to_feature_tuple(input_json) ==
        {'current_balance': 9270.02, 'fico_score': 476,
         'max_bal_l30': 11567.11, 'min_bal_l30': 9270.02,
         'sum_credit_l30': 0, 'sum_debit_l30': 2297.09,
         'catg_max_debits': 'XXX-33'})
