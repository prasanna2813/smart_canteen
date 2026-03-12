from flask import Flask,render_template,request,redirect,url_for
import mysql.connector
import random

app = Flask(__name__)



db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="smart_canteen"
)

cursor = db.cursor()



cart = []
current_user = ""



@app.route("/")
def home():
    return render_template("index.html")




@app.route("/login")
def login():
    return render_template("login.html")




@app.route("/user", methods=["POST"])
def user():

    global current_user

    roll = request.form["roll"]
    password = request.form["password"]

    current_user = roll

    return render_template("userpanel.html",roll=roll)




@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():

    item = request.form["item"]
    price = int(request.form["price"])
    quantity = int(request.form["quantity"])

    total = price * quantity

    cart_item = {
        "item":item,
        "price":price,
        "quantity":quantity,
        "total":total
    }

    cart.append(cart_item)

    return redirect("/cart")




@app.route("/cart")
def view_cart():

    total_price = sum(item["total"] for item in cart)

    return render_template("cart.html",cart=cart,total=total_price)



@app.route("/bill")
def bill():

    total_price = sum(item["total"] for item in cart)

    return render_template("bill.html",cart=cart,total=total_price)



@app.route("/payment")
def payment():

    total_price = sum(item["total"] for item in cart)

    return render_template("payment.html",total=total_price)




@app.route("/success")
def success():

    global current_user

    token = random.randint(100,999)

    for item in cart:

        cursor.execute(
        "INSERT INTO orders (roll_number,item,price,quantity,total,token) VALUES (%s,%s,%s,%s,%s,%s)",
        (current_user,item["item"],item["price"],item["quantity"],item["total"],token)
        )

    db.commit()

    cart.clear()

    return render_template("success.html",token=token)



@app.route("/admin")
def admin():
    return render_template("adminlogin.html")




ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

@app.route("/adminlogin", methods=["POST"])
def adminlogin():

    username = request.form["username"]
    password = request.form["password"]

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return render_template("admindashboard.html")
    else:
        return "Invalid Admin Login"




@app.route("/dashboard")
def dashboard():

    cursor.execute("SELECT * FROM orders")

    orders = cursor.fetchall()

    cursor.execute("SELECT SUM(total) FROM orders")

    total_sales = cursor.fetchone()[0]

    total_orders = len(orders)

    return render_template(
        "admindashboard.html",
        orders=orders,
        total_sales=total_sales,
        total_orders=total_orders
    )
@app.route("/menu")
def menu():
    return render_template("userpanel.html")


@app.route("/delete/<int:id>")
def delete_order(id):

    cursor.execute("DELETE FROM orders WHERE id=%s",(id,))
    db.commit()

    return redirect("/dashboard")




if __name__ == "__main__":
    app.run(debug=True)