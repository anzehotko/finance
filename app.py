import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
os.environ["API_KEY"] = "pk_f5cc891004b4472d92bd7064e9ec8ac7"
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Check if table purchases exists
    check = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='purchases'")
    if len(check) > 0:
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        table = db.execute("SELECT symbol, SUM(number) FROM purchases WHERE username = ? GROUP BY symbol", username)
        list1 = []
        sum_stocks = 0
        for row in table:
            dict = {}
            stock_inf = lookup(row["symbol"])
            cur_price = stock_inf["price"]
            total_value = float(cur_price) * int(row["SUM(number)"])
            dict["symbol"] = row["symbol"]
            dict["number"] = row["SUM(number)"]
            dict["price"] = cur_price
            dict["total_value"] = total_value
            list1.append(dict)
            sum_stocks += float(row["SUM(number)"])*float(cur_price)

        balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        gr_total = sum_stocks + balance
        return render_template("/index.html", list1=list1, gr_total=gr_total, balance=balance)
    else:
        return render_template("/index1.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Check if the input is blank  and render an apology!
        if not request.form.get("symbol"):
            return apology("must provide symbol")
        if lookup(request.form.get("symbol")) == None:
            return apology("the provided symbol does not exist")
        if not request.form.get("shares"):
            return apology("please input a number of stocks you wish to buy")
        if request.form.get("shares").isnumeric() == False:
            return apology("sorry, only numeric values are acceptable")
        if float(request.form.get("shares")) <1:
            return apology("number of shares must be a positive integer")
        if float(request.form.get("shares")) % 1 != 0:
            return apology("number of shares must be a positive integer")


        # Get the wanted stock information and store it into a variable
        stockinf = lookup(request.form.get("symbol"))
        cur_price = stockinf["price"]
        num_stocks = float(request.form.get("shares"))

        bal = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        balance = bal[0]["cash"]

        user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        username = user[0]["username"]
        symbol = request.form.get("symbol").upper()
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        action = "buy"



        # Inserting new data into a table of purchases
        check2 = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='purchases'")
        if len(check2) > 0:
            if int(num_stocks)*float(cur_price) > float(balance):
                return apology("you do not have enough money to buy this number of stocks at current price")
            new_balance = float(balance) - (float(num_stocks)*float(cur_price))
            db.execute("UPDATE users SET cash=? WHERE id=?", new_balance, session["user_id"])
            db.execute("INSERT INTO purchases (username, symbol, number, price, timestamp, action) VALUES(?, ?, ?, ?, ?, ?)", username, symbol, num_stocks, cur_price, timestamp, action)
            return redirect("/")
        else:
            if int(num_stocks)*int(cur_price) > float(balance):
                return apology("you do not have enough money to buy this number of stocks at current price")
            new_balance = float(balance) - (int(num_stocks)*float(cur_price))
            db.execute("UPDATE users SET cash=? WHERE id=?", new_balance, session["user_id"])
            db.execute("CREATE TABLE purchases (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT NOT NULL, symbol TEXT NOT NULL, number NUMERIC NOT NULL, price NUMERIC NOT NULL, timestamp TEXT NOT NULL, action TEXT NOT NULL)")
            db.execute("CREATE INDEX symbol ON purchases(symbol)")
            db.execute("CREATE INDEX timestamp ON purchases(timestamp)")
            db.execute("INSERT INTO purchases (username, symbol, number, price, timestamp, action) VALUES(?, ?, ?, ?, ?, ?)", username, symbol, num_stocks, cur_price, timestamp, action)

            return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    check2 = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='purchases'")
    if len(check2) > 0:
        username = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])[0]["username"]
        tableh = db.execute("SELECT symbol, number, price, timestamp, action FROM purchases WHERE username=?", username)
        return render_template("history.html", tableh=tableh)
    else:
        return render_template("nohistory.html")


@app.route("/addcash", methods=["GET", "POST"])
@login_required
def addcash():
    """Add cash as you wish"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if int(request.form.get("amount")) <= 0:
            return apology("please input a positive amount")
        bal = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        balance = bal[0]["cash"]
        amount = request.form.get("amount")
        new_balance = float(balance) + int(amount)
        db.execute("UPDATE users SET cash=? WHERE id=?", new_balance, session["user_id"])
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("addcash.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        # Check that symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol")

        # Get the wanted stock information and store it into a variable
        stockinf = lookup(request.form.get("symbol"))

        if stockinf == None:
            return apology("this symbol does not exist")

        return render_template("quoted.html", stockinf=stockinf)


    else:
        return render_template("quote.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username doesn't already exist
        if len(rows) != 0:
            return apology("username already exists")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Ensure password and confirmation match
        if request.form.get("confirmation") != request.form.get("password"):
            return apology("password and confirmation do not match!")

        # Add the user's entry into the database
        # Getting username and password from forms in "register.html" and storing them in separate variables.
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))


        # Insert new submission into SQL database!
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Check if the input number is bigger than actual number of owned said stocks.!
        symbol = request.form.get("symbol")
        username = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])[0]["username"]
        checkn = db.execute("SELECT SUM(number) FROM purchases WHERE symbol=? AND username=?", symbol, username)[0]["SUM(number)"]
        if int(request.form.get("shares"))>int(checkn):
            return apology("sorry, you do not own that many of said stocks")
        if int(request.form.get("shares"))<=0:
            return apology("sorry, please input a positive number")

        cur_price = lookup(request.form.get("symbol"))["price"]
        bal = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        balance = bal[0]["cash"]
        num_stocks = request.form.get("shares")

        username = db.execute("SELECT username FROM users WHERE id=?", session["user_id"])[0]["username"]
        sold_num = -int(num_stocks)
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        action = "sell"

        new_balance = float(balance) + (float(num_stocks)*float(cur_price))
        db.execute("UPDATE users SET cash=? WHERE id=?", new_balance, session["user_id"])
        db.execute("INSERT INTO purchases (username, symbol, number, price, timestamp, action) VALUES(?, ?, ?, ?, ?, ?)", username, symbol, sold_num, cur_price, timestamp, action)
        return redirect("/")




    else:
        check0 = db.execute("SELECT symbol FROM purchases GROUP BY symbol")
        return render_template("sell.html", check0=check0)
