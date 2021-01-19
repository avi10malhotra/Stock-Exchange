from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    """Display User's Portfolio"""

    portfolio_info = db.execute("SELECT symbol, shares FROM portfolio WHERE id = :id", \
                                id= session["user_id"])

    # temp variable to store total cash
    grand_total = 0

    # update user's portfolio
    for info in portfolio_info:
        symbol = info["symbol"]
        shares = info["shares"]
        stock = lookup(symbol)
        total = shares * stock["price"]
        grand_total += total
        db.execute("UPDATE portfolio SET price =:price, total =:total, name =:name \
                                        WHERE id =:id AND symbol =:symbol", \
                                        price = stock["price"], total = total, name = stock["name"], \
                                        id = session["user_id"], symbol = symbol)

    # update user's cash and total cash
    latest_cash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
    grand_total += latest_cash[0]["cash"]

    # display all information on the page
    latest_portfolio = db.execute("SELECT * from portfolio WHERE id=:id", id=session["user_id"])
    return render_template("index.html", stocks= latest_portfolio, \
                            cash= latest_cash[0]["cash"], total= grand_total )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""

    if request.method == "POST":

        # use lookup function to get stock info, and validate proper symbol
        quote = lookup(request.form.get("symbol"))
        if not quote:
            return apology("You have selected an invalid symbol")

        # validate number of shares
        shares = float(request.form.get("shares"))
        if shares < 0:
            return apology("Last time I checked, shares were positive integers")

        # select user's cash via a command
        cash = db.execute("SELECT cash FROM users WHERE id= :id", \
                            id= session["user_id"])

        # calculate user's cost
        price = round(float(quote["price"]))
        cost = round(float(shares * price))

        # check if user can make the transaction
        if cash[0]["cash"] < cost:
            return apology("You do not have enough money")

        # make the following queries
        else:
            # update user's cash
            db.execute("UPDATE users SET cash = cash - :cost WHERE id = :id", \
                        cost= cost, id= session["user_id"])

            # update user's portflio
            db.execute("UPDATE portfolio SET shares = shares + :shares WHERE id = :id AND symbol = :symbol", \
                        id=session["user_id"],symbol= quote["symbol"],shares= shares)

            # insert the number of shares into a user's portfolio, else just increment the share count
            db.execute("INSERT OR IGNORE INTO portfolio (id,symbol,shares) VALUES (:id,:symbol,:shares)", \
                        id= session["user_id"],symbol=quote["symbol"],shares=shares)

            # record user's transaction
            db.execute("INSERT INTO history (id,symbol,shares,price,date) \
                        VALUES (:id,:symbol,:shares,:price,datetime('now'))", \
                        id= session["user_id"], symbol= quote["symbol"], shares= shares, price= price)

        return redirect(url_for("index"))

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    history = db.execute("SELECT symbol, shares, price, date FROM history WHERE id = :id", id=session["user_id"])

    # display all transcations in history
    for transaction in history:
        symbol = transaction["symbol"]
        shares = transaction["shares"]
        price = transaction["price"]
        date = transaction["date"]

    return render_template("history.html", history = history)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", \
                            username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # if user has reached route via POST
    if request.method == "POST":
        result = lookup(request.form.get("symbol"))

        if not result:
            return apology("Invalid stock symbol")

        # return information about the stock
        return render_template("quoted_stock.html", stock=result)

    # if user has reached the route via GET, redirect
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # if user has reached route via POST
    if request.method == "POST":

        # ensure username submition
        if not request.form.get("username"):
            return apology("Please submit a username!")

        # ensure password submition
        elif not request.form.get("password"):
            return apology("Please submit a password!")

        # verify the password
        elif request.form.get("password") != request.form.get("password_confirm"):
            return apology("Your passwords do not match!")

        # encrpyt the password and store the hash
        password = request.form.get("password")
        hash = pwd_context.hash(password)

        # proceed and register the user in
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", \
                            username=request.form.get("username"), hash= hash)

        # check if username already exists
        if not result:
            return apology("Username already exists, please choose a new useranme")

        # remember session ID and redirect to index page
        session["user_id"] = result
        return redirect(url_for("index"))

    # if user has reached the route via GET, redirect
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method == "POST":

        # check user input
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("Please provide some input")

        quote = lookup(request.form.get("symbol"))
        if quote == None:
            return apology("Invalid symbol")
        if not request.form.get("shares").isdigit():
            return apology("Positive integer needed")

        shares = int(request.form.get("shares"))
        stocks = []

        # check user's portfolio
        stocks = db.execute("SELECT shares FROM portfolio WHERE id = :id AND symbol = :symbol", id=session["user_id"], symbol = quote["symbol"])
        if stocks == []:
            return apology("How can you sell something you do not own?")
        if shares > stocks[0]["shares"]:
            return apology("You do not own that many stocks")

        # calculate total cost
        price = round(float(quote["price"]))
        cost = round(float(shares * price))

        # update user's information
        db.execute("UPDATE users SET cash = cash + :cost WHERE id = :id", cost = cost, id=session["user_id"])
        if shares < stocks[0]["shares"]:
            db.execute("UPDATE portfolio SET shares = shares - :shares WHERE id = :id AND symbol = :symbol", \
                        id=session["user_id"], shares = shares, symbol = quote["symbol"])
        elif shares == stocks[0]["shares"]:
            db.execute("DELETE FROM portfolio WHERE id = :id AND symbol = :symbol", \
                        id=session["user_id"], symbol = quote["symbol"])

        # record the transcation in history
        db.execute("INSERT INTO history (id,symbol,shares,price,date) \
                    VALUES (:id,:symbol,:shares,:price,datetime('now'))", \
                    id=session["user_id"], symbol=quote["symbol"], shares= -shares, price =price)

        return redirect(url_for("index"))

    else:
        return render_template("sell.html")

@app.route("/settings", methods=["GET","POST"])

def settings():
    """Additional feature - Change user password"""

    if request.method == "POST":

        # check user input
        if not request.form.get('password'):
            return apology("Please provide your current password")

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]['hash']):
            return apology("Current password is invalid")

        # ensure new password submission
        if not request.form.get("new-password"):
            return apology("Please provide your new password")
        if not request.form.get("password-confirm"):
            return apology("Please confirm you password")

        # verify user's password
        if request.form.get("new-password") != request.form.get("password-confirm"):
            return apology("Your passwords do not match")

        # store the password as a hash and update it
        password = request.form.get("new-password")
        hash = pwd_context.hash(password)
        result = db.execute("UPDATE users SET hash=:hash", hash=hash)

        return redirect(url_for("index"))

    else:
        return render_template("settings.html")


