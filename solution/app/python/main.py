import json
import pandas as pd
import datetime as dt
from sklearn.externals import joblib
from flask import Flask, request, abort, jsonify, make_response


def _get_date_only(input_datetime=dt.datetime.today()):
    return (input_datetime
            .replace(hour=0, minute=0, second=0,
                     microsecond=0, tzinfo=None))


def _float_to_dollar(input_float):
    return float("%.2f" % input_float)


def raw_data_to_feature_tuple(raw_data_json):

    # Note on Code Style
    # We will be following the Early Exit (Return) Strategy here as
    # there can be multiple error conditions and nesting will cause
    # too much branching

    # Creating Blank JSON
    result_json = {}

    # Adding in the simple components (Current Balance and FICO Score)
    try:
        result_json['current_balance'] = _float_to_dollar(
            raw_data_json['CurrentBalance'])
        result_json['fico_score'] = raw_data_json['FICOScore']
    except Exception:
        raise KeyError

    # Checking if Transactions Exist. If not, return appropriate json
    if len(raw_data_json['Transactions']) == 0:
        try:
            result_json['max_bal_l30'] = _float_to_dollar(
                raw_data_json['CurrentBalance'])
            result_json['min_bal_l30'] = _float_to_dollar(
                raw_data_json['CurrentBalance'])
        except Exception:
            raise KeyError
        result_json['sum_debit_l30'] = 0
        result_json['sum_credit_l30'] = 0
        result_json['catg_max_debits'] = 'None'
        return result_json

    # Picking up the Transactions as a Pandas DataFrame if Exists
    try:
        transactions_df = pd.DataFrame.from_records(
            data=raw_data_json['Transactions'],
            exclude=["TransactionID"])
    except Exception:
        raise KeyError

    # Converting Type to lowercase
    try:
        transactions_df.PostDate = pd.to_datetime(transactions_df.PostDate)
        transactions_df.Type = transactions_df.Type.str.lower()
    except Exception:
        raise KeyError

    # Category with Maximum Debits
    category_debits = (
        transactions_df
        .loc[
            (transactions_df['Type'] == 'debit'),
            ['Category', 'Amount']])
    try:
        result_json['catg_max_debits'] = (
            category_debits
            .loc[category_debits.Amount.idxmax(), 'Category'])
    except ValueError:
        result_json['catg_max_debits'] = "None"

    # Filtering Down to Last 30 Days with Entries for each day
    last_30_days = pd.DataFrame(
        data=[_get_date_only() - dt.timedelta(days=date_offset)
              for date_offset in range(0, 30)],
        columns=['PostDate'])
    balance_df_l30 = (
        last_30_days
        .merge(right=transactions_df, how='left',
               on='PostDate', sort=True))

    # Checking for Transactions in Last 30 Days. If none, set appropriate result
    if all(pd.isna(balance_df_l30.Type)):
        try:
            result_json['max_bal_l30'] = _float_to_dollar(
                raw_data_json['CurrentBalance'])
            result_json['min_bal_l30'] = _float_to_dollar(
                raw_data_json['CurrentBalance'])
        except Exception:
            raise KeyError
        result_json['sum_debit_l30'] = 0
        result_json['sum_credit_l30'] = 0
        return result_json

    # Sorting by PostDate and Type
    balance_df_l30 = (balance_df_l30
                      .sort_values(by=['PostDate', 'Type'])
                      .reset_index(drop=True))

    # Creating Signed Amount
    balance_df_l30['Signed_Amount'] = (
        balance_df_l30.Amount
        .where(cond=(balance_df_l30['Type'] == 'credit'),
               other=(-balance_df_l30.Amount)))

    # Creating Account Balance assuming initial Zero Balance
    balance_df_l30['cum_sum_amount'] = balance_df_l30.Signed_Amount.fillna(
        0).cumsum()

    # Calculating Initial Balance based on
    # Gap between Final CumSum and Current Balance
    final_cum_sum = (
        balance_df_l30
        .loc[balance_df_l30.cum_sum_amount.last_valid_index(),
             'cum_sum_amount'])

    initial_balance = result_json['current_balance'] - final_cum_sum

    # Calculating Correct Balance
    balance_df_l30['balance_amount'] = (balance_df_l30['cum_sum_amount'] +
                                        initial_balance)

    # Maximum Balance Over Last 30 Days
    result_json['max_bal_l30'] = _float_to_dollar(
        balance_df_l30.balance_amount.max())

    # Minimum Balance Over Last 30 Days
    result_json['min_bal_l30'] = _float_to_dollar(
        balance_df_l30.balance_amount.min())

    # Sum of Debits and Credits over Last 30 Days
    debits_and_credits = (
        balance_df_l30[['Type', 'Amount']]
        .groupby('Type').sum())
    try:
        result_json['sum_debit_l30'] = _float_to_dollar(
            debits_and_credits.loc['debit', 'Amount'])
    except KeyError:
        result_json['sum_debit_l30'] = 0

    try:
        result_json['sum_credit_l30'] = _float_to_dollar(
            debits_and_credits.loc['credit', 'Amount'])
    except KeyError:
        result_json['sum_credit_l30'] = 0

    # Results!
    return result_json


def generate_prediction(raw_data_json):
    # # current balance; current_balance
    # # maximum balance over last 30 days; max_bal_l30
    # # minimum balance over last 30 days; min_bal_l30
    # # sum of debits over last 30 days; sum_debit_l30
    # # sum of credits over last 30 days; sum_credit_l30
    # # category which had maximum debits (or the string "None" if there were no debits); catg_max_debits
    # # FICO score. fico_score

    feature_json = raw_data_to_feature_tuple(raw_data_json)

    encoding_pipeline = joblib.load("resources/encoder_pipeline.pkl")

    encoded_features = encoding_pipeline.fit_transform([[
        feature_json['current_balance'],
        feature_json['max_bal_l30'],
        feature_json['min_bal_l30'],
        feature_json['sum_debit_l30'],
        feature_json['sum_credit_l30'],
        feature_json['catg_max_debits'],
        feature_json['fico_score']
    ], ])

    prediction_pipeline = joblib.load("resources/model_pipeline.pkl")

    prediction = prediction_pipeline.predict(encoded_features)[0]

    response = str(prediction)

    return response


# Creating Flask Instance
app = Flask(__name__)


# Creating a Bad Request Handler
def bad_request(message, include_body_sample=True):
    body_sample = {
        "UserID":  "12345678-1234-5678-1234-567812345678",
        "CurrentBalance":  42.82,
        "FICOScore": 682,
        "Transactions": [
            {"TransactionID": "ABCDEF12-3456-78AB-CDEF12345678",
             "Amount":        123.45,
             "Category":      "Entertainment",
             "Type":          "debit",
             "PostDate":      "2018-06-01"
             },
            {"TransactionID": "9ABCDEF0-1234-5678-9ABCDEF012345",
             "Amount":        2048.64,
             "Category":      "Deposits",
             "Type":          "credit",
             "PostDate":      "2018-06-02"
             }
        ]
    }

    response_json = {'error_code': 400,
                     'error_message': message}

    if include_body_sample:
        response_json['body_sample'] = body_sample

    response = jsonify(response_json)
    return abort(make_response((response, 400, [])))


def process_request(request_json):
    if not request_json.get('CurrentBalance'):
        return bad_request("CurrentBalance is missing from Body")

    if not request_json.get('FICOScore'):
        return bad_request("FICOScore is missing from Body")

    if (not request_json.get('Transactions')) and (request_json.get('Transactions') != []):
        return bad_request("Transactions is missing from Body. If there are no transactions, add an empty element")

    if not isinstance(request_json.get('Transactions'), list):
        return bad_request("Transactions needs to be a list element")

    try:
        prediction = generate_prediction(request_json)
    except Exception as e:
        print str(e)
        return bad_request("Generating Predictions Failed", include_body_sample=False)

    return {"UserID": request_json.get('UserID'), 'prediction': prediction}

# Creating End Point
@app.route('/predictions', methods=['POST'])
def main():
    if not request.json:
        return bad_request("Please add Data JSON to request Body")

    request_json = request.get_json(force=True, silent=True)

    # If it is a single request
    if isinstance(request_json, dict):
        return jsonify(process_request(request_json))
    # If there are multiple Requests
    elif isinstance(request_json, list):
        responses = [process_request(req_json) for req_json in request_json]
        return jsonify(responses)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
