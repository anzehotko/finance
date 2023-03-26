# FINANCE

#### Description:
Finance is a webpage containing stock data and allows users to buy and sell (fictionally) stocks at their actual current real-world prices and keep ttrack of theeir financial portfolio. The project was created using the following technologies:
- Python with flask (accessing stock prices data of https://iexcloud.io/ through API keys)
- SQL Lite
- Html
- Bootstrap
- CSS

HOW THE WEBPAGE IS USED

The index page of the webpage prompts the user to login or register if they do not have an account yet. Once logged in, the user can see their portfolio, meaning the number of stocks owned, their price and the value of holding. Also, the cash balance and the grand total are displayed. To check the current prices of stocks, the user must click on the "Quote" button in the upper left corner. To find the price of a stock, the user enters a symbol for that said stock and clicks on search.
To buy a certain stock, the user should click on the "Buy" button, where prompted to input the symbol of the stock and number of stocks he wishes to buy. If the cash balance of the user is large enough, the purchase comes through and new data is stored in the SQL database, updating the user's portfolio. The user is redirected to the portfolio page, where the updated data is displayed.
To sell stocks, a similar mechanism is in place, only that when choosing which stock to sell there is already a drop-down menu provided which is based of the data stored in SQL tables and displays only the stocks currently owned by the user. If the number of stocks the user wants to sell is not larger than the number of stocks owned, the sell goes through and the user is once again redirected to the portfolio page.
There is also an option of seeing the history of buying/selling stocks. To access the data, the user should click on the "History" button, where data is displayed in a table fashion. The records of dates and times of the purchases that were previously stored in the SQL database are now also displayed along side each action. Date and time variables are stored with the help of the "datetime" module in python.
To add more money to the user's cash balance, there is an option of "Add cash". The user inputs the amount of dollars he wishes to add to his balance and confirms. The now updated SQL data of the user's cash balance gets rendered once again.
If any of the previously mentioned actions do not come through because of various reasons (not enough cash, wrong input information, searching for stock symbols that don't exist etc.) an apology with a suitable explanation gets rendered.














