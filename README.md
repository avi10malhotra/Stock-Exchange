# Stock Exchange website
Designed a web-app which enables users to virtually buy and sell stocks. The app uses real world stock pricing from Yahoo Finance.
<br><br>
"CS50 Finance", a problem set from the HarvardX CS50 course, provides the foundation code for this project. For more information, click [here](https://docs.cs50.net/problems/finance/finance.html). If you to wish to view the model solution, click [here](https://finance.cs50.net/login).
## Background
This web-app allows one to manage portfolios of stocks, including features that allow users to hypothetically 'buy' and 'sell' stocks. 
<br><br>
The prices of these stocks are queried via [Yahoo Finance](http://finance.yahoo.com/), which allows a retrieval of stock quotes in Comma Separated Values (CSV) format via URLs. It is worth mentioning that the URL returned comprises of 3 HTTP parameters: **_s, f,_** and _**e**_, which specify the stock symbol, stock data reference, and file format respectively.  

## Project Files
### static/
This folder contains only one file, **styles.css** which render the default styling for the web app. 
### templates/
All files in this folder are HTML markups that have been stylised with [**Bootstrap**](https://getbootstrap.com/), a front-end open source toolkit that provides incredibly responsive JavaScript plugins. All of these templates are rendered and called from **application.py**,  thereby allowing relaying of messages from different routes and flashing the said messages to the user. 
### finance. db
The database that encapsulates a table called _users_. Its schema specifies that each registered user receives 10k USD in cash.  All routes implemented in **application.py** query this file via the _db.execute_ command from the CS50 library.
### helpers.py
A helper file provided with the problem set material that defines some functions and/or their decorators, namely _apology, login_required,  lookup,_ and _usd_.
### application.py
The backbone of the Stock Exchange website. It uses [Flask](http://flask.pocoo.org/),  such that it allows storing user sessions on the local filesystem. Moreover, this file is also primarily responsible for making amendments to **finance.db**. This file defines the following routes:

 - Register:
 - Quote:
 - Buy:
 - Index:
 - Sell:
 - History:
 - Password update: 
