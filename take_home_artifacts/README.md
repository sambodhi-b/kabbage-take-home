# Machine Learning Engineer Take-Home

The following is a take-home coding exercise. You will have 24 hours to complete
it, though we expect it will take considerably less time.

NOTE: ANY CODE TAKEN FROM A NON-API SOURCE MUST BE CITED! 
Any submission that does not cite a source, whether it's Kaggle, Stack Overflow, 
or other data science sites, WILL BE IMMEDIATELY REJECTED with no exceptions. 
We recommend citing API sources just to avoid confusion. 
Also cite any git repos, including your own, that you have used. 

## Description
Part of what gives Kabbage an edge over its competitors is the ability to
quickly qualify customers for a loan. To that end, Kabbage maintains web 
services that can score a customer against one of myriad models.

Your task is to create a web service that can do two things:
- Transform a list of transactions into a feature set for a model;
- Execute a model based on the feature set, which will return a floating point
  number.

The web service must have a REST API that has one or more endpoints - 
the service can combine the functions into one endpoint, split them
into two endpoints, or split them into multiple endpoints.
The only restriction on the API's design is that one endpoint must be
able to transform the raw data (format defined below), and some endpoint
(possibly the same one) must return the model's prediction.

Your solution should address the following:
- How does the web service manage load?
- How does the solution measure and optimize performance?
- How does the web service handle and monitor resource consumption?
- What kinds of errors does the service handle, and how does it handle them?
- How do you guarantee that the service will be stable?

Whether you have enough time to address all of these in code or not, your
solution should include a README.md that addresses these concerns.


## Raw Data Format:

You will be given raw data for each customer that includes information used
in the scoring request. The scoring request's raw data looks like the following:
```
{
    "UserID":  "12345678-1234-5678-1234-567812345678",
    "CurrentBalance":  42.82,
    "FICOScore": 682,
    "Transactions": [
        { "TransactionID": "ABCDEF12-3456-78AB-CDEF12345678",
          "Amount":        123.45,
          "Category":      "Entertainment",
          "Type":          "debit",
          "PostDate":      "2018-06-01"
        },
        { "TransactionID": "9ABCDEF0-1234-5678-9ABCDEF012345",
          "Amount":        2048.64,
          "Category":      "Deposits",
          "Type":          "credit",
          "PostDate":      "2018-06-02"
        }
    ]
}
```
The fields have the following meaning:
- UserID: a unique string for the user being scored;
- CurrentBalance: the user's account balance at the end of the interval;
- FICOScore: the user's current FICO score, an integer between 0 and 850;
- Transactions: a list of zero or more transactions;
    - TransactionID: a unique string for the transaction;
    - Amount: the transaction's amount;
    - Category: the transaction's category, which is one of 57 values
      (see transactions.md for more information);
    - Type: "debit" (for money going out of the account) or 
            "credit" (for money going into the account);
    - PostDate: the date at which the money was added or removed from the
                account. You can assume that, if multiple transactions occur on
                the same date, the credits are processed before the debits.


## Model Prediction

The model has been written in Python and has been saved as a pickled object in
the file "sample_model.pkl.gz" (which you will need to unzip). It is a scikit-learn 
Pipeline object that has a single relevant method, predict(), that will take 
a list of the following arguments, in this order:

- current balance;
- maximum balance over last 30 days;
- minimum balance over last 30 days;
- sum of debits over last 30 days;
- sum of credits over last 30 days;
- category which had maximum debits (or the string "None" if there were no debits);
- FICO score.

The "predict" method returns a two-element list: 
- entry 0 is the probability that the user will not default;
- entry 1 is the probability that the user will default.


## Deliverables
Your package should include the following:
- the web service's code, in the language of your choice;
- any tests that are external to the service itself;
- a README.md that includes your thinking, design, how to run the web service,
  and how to run tests, if any.


## What does a great submission look like?
- The REST API has a rationale to it and is easy to understand.
- The web service describes how to handle load, including how to handle
  simultaneous requests.
- Features are correctly calculated from raw data.
- Code is well-structured, easy to read, and commented well.
- There is an understanding of what makes a system performant, 
  easy to manage, and easy to debug.
- The service is robust and handles errors from common conditions well.
- There are tests that give the confidence to deploy the service to production.
