import json
import pandas as pd
import datetime as dt


def _get_date_only(input_datetime=dt.datetime.today()):
    return (input_datetime
            .replace(hour=0, minute=0, second=0,
                     microsecond=0, tzinfo=None))

def _float_to_dollar(input_float):
    return float("%.2f" % input_float)


def raw_data_to_feature_tuple(raw_data_json):
    # # current balance;
    # # maximum balance over last 30 days;
    # # minimum balance over last 30 days;
    # # sum of debits over last 30 days;
    # # sum of credits over last 30 days;
    # - category which had maximum debits (or the string "None" if there were no debits);
    # # FICO score.

    # Note on Code Style
    # We will be following the Early Exit (Return) Strategy here as
    # there can be multiple error conditions and nesting will cause
    # too much branching

    # Creating Blank JSON
    result_json = {}

    # Adding in the simple components (Current Balance and FICO Score)
    # TODO Exception Handling
    result_json['current_balance'] = _float_to_dollar(raw_data_json['CurrentBalance'])
    result_json['fico_score'] = raw_data_json['FICOScore']

    # Checking if Transactions Exist. If not, return appropriate json
    if len(raw_data_json['Transactions']) == 0:
        result_json['max_bal_l30'] = _float_to_dollar(raw_data_json['CurrentBalance'])
        result_json['min_bal_l30'] = _float_to_dollar(raw_data_json['CurrentBalance'])
        result_json['sum_debit_l30'] = 0
        result_json['sum_credit_l30'] = 0
        result_json['catg_max_debits'] = 'None'
        return result_json

    # Picking up the Transactions as a Pandas DataFrame if Exists
    transactions_df = pd.DataFrame.from_records(
        data=raw_data_json['Transactions'],
        exclude=["TransactionID"])

    # Converting Type to lowercase
    transactions_df.PostDate = pd.to_datetime(transactions_df.PostDate)
    transactions_df.Type = transactions_df.Type.str.lower()

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
        result_json['max_bal_l30'] = _float_to_dollar(raw_data_json['CurrentBalance'])
        result_json['min_bal_l30'] = _float_to_dollar(raw_data_json['CurrentBalance'])
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
    balance_df_l30['cum_sum_amount'] = balance_df_l30.Signed_Amount.fillna(0).cumsum()

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
    result_json['max_bal_l30'] = _float_to_dollar(balance_df_l30.balance_amount.max())

    # Minimum Balance Over Last 30 Days
    result_json['min_bal_l30'] = _float_to_dollar(balance_df_l30.balance_amount.min())

    # Sum of Debits and Credits over Last 30 Days
    debits_and_credits = (
        balance_df_l30[['Type', 'Amount']]
        .groupby('Type').sum())
    try:
        result_json['sum_debit_l30'] = _float_to_dollar(debits_and_credits.loc['debit', 'Amount'])
    except KeyError:
        result_json['sum_debit_l30'] = 0

    try:
        result_json['sum_credit_l30'] = _float_to_dollar(debits_and_credits.loc['credit', 'Amount'])
    except KeyError:
        result_json['sum_credit_l30'] = 0

    # Results!
    return result_json
