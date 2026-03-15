from flask import Flask, render_template, request, redirect
import sqlite3
import random

app = Flask(__name__)

cart = []
current_user = ""

# ---------------- DATABASE ----------------

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
roll TEXT,
item TEXT,
price INTEGER,
qty INTEGER,
total INTEGER,
status TEXT,
token INTEGER
)
""")

conn.close()


def get_db():
    return sqlite3.connect("database.db")


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- USER LOGIN ----------------

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login_check", methods=["POST"])
def login_check():

    global current_user

    roll = request.form["roll"]
    password = request.form["password"]

    if len(roll) == 6 and password == "svce@1999":
        current_user = roll
        return redirect("/userpanel")
    else:
        return "Invalid Login"


# ---------------- USER PANEL ----------------

@app.route("/userpanel")
def userpanel():
    return render_template("userpanel.html")


# ---------------- ADD TO CART ----------------

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():

    item = request.form["item"]
    price = int(request.form["price"])
    qty = int(request.form["quantity"])

    total = price * qty

    cart.append([item, price, qty, total])

    return redirect("/cart")


# ---------------- CART PAGE ----------------

@app.route("/cart")
def cart_page():

    total = sum(i[3] for i in cart)

    return render_template("cart.html", cart=cart, total=total)


# ---------------- CHECKOUT → PAYMENT ----------------

@app.route("/checkout")
def checkout():

    total = sum(i[3] for i in cart)

    return render_template("payment.html", total=total)


# ---------------- PAYMENT DONE ----------------

@app.route("/paydone")
def paydone():

    conn = get_db()
    cur = conn.cursor()

    token = random.randint(100,999)

    for item in cart:
        cur.execute(
        "INSERT INTO orders(roll,item,price,qty,total,status,token) VALUES(?,?,?,?,?,?,?)",
        (current_user,item[0],item[1],item[2],item[3],"Pending",token)
        )

    conn.commit()
    conn.close()

    cart.clear()

    return redirect(f"/success/{token}")


# ---------------- SUCCESS PAGE ----------------

@app.route("/success/<token>")
def success(token):
    return render_template("success.html",token=token)


# ---------------- USER ORDER TRACK ----------------

@app.route("/userorders")
def userorders():

    conn = get_db()
    cur = conn.cursor()

    orders = cur.execute(
        "SELECT * FROM orders WHERE roll=?",
        (current_user,)
    ).fetchall()

    conn.close()

    return render_template("userorders.html", orders=orders)

# ---------------- ADMIN LOGIN ----------------

@app.route("/adminlogin")
def adminlogin():
    return render_template("adminlogin.html")


@app.route("/admin_check", methods=["POST"])
def admin_check():

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":
        return redirect("/admin")
    else:
        return "Invalid Admin Login"


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin")
def admin():

    conn = get_db()
    cur = conn.cursor()

    orders = cur.execute("SELECT * FROM orders").fetchall()

    total_orders = len(orders)
    total_sales = sum(i[5] for i in orders)

    conn.close()

    return render_template(
        "admindashboard.html",
        orders=orders,
        total_orders=total_orders,
        total_sales=total_sales
    )


# ---------------- UPDATE QUANTITY ----------------

@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    qty = int(request.form["qty"])

    conn = get_db()
    cur = conn.cursor()

    price = cur.execute(
        "SELECT price FROM orders WHERE id=?",
        (id,)
    ).fetchone()[0]

    total = price * qty

    cur.execute(
        "UPDATE orders SET qty=?, total=? WHERE id=?",
        (qty, total, id)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- ACCEPT ORDER ----------------

@app.route("/accept/<int:id>")
def accept(id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE orders SET status='Accepted' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- ORDER READY ----------------

@app.route("/reached/<int:id>")
def reached(id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE orders SET status='Reached' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- DELETE ORDER ----------------

@app.route("/delete/<int:id>")
def delete(id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM orders WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)