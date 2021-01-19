import csv
import urllib.request
import yfinance as yf

from flask import redirect, render_template, request, session, url_for
from functools import wraps

def apology(top="", bottom=""):
    """Renders message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
            ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=escape(top), bottom=escape(bottom))

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def lookup(symbol):
    """Look up quote for symbol."""

    # reject symbol if it starts with caret
    if symbol.startswith("^"):
        return None

    # reject symbol if it contains comma
    if "," in symbol:
        return None

    # https://github.com/ranaroussi/yfinance
    # query the yfinance module (which wraps the Yahoo Finance API)
    try:
        stock = yf.Ticker("{}".format(symbol))
        data = stock.info
    except:
        return None


    # return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
    return {
        "name": data['shortName'],
        "price": data['regularMarketPrice'],
        "symbol": data['symbol'].upper()
    }

def usd(value):
    """Formats value as USD."""
    return "${:,.2f}".format(value)
