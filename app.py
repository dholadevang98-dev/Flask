import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
UPLOAD_FOLDER = "static/images/products"
app.secret_key = "secretkey123"



app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Devang@123'
app.config['MYSQL_DB'] = 'login'

mysql = MySQL(app)

@app.route('/register')
def register_page():
    return render_template("register.html")
@app.route('/')
def login_page():
    return render_template("login.html")
@app.route('/admin_login')
def admin_page():
    return render_template("admin_login.html")




@app.route('/index')
def welcome():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()

    print(products)

    for product in products:
        print(product)

    return render_template("/index.html", products=products)
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form["product_name"]
        price = request.form["price"]
        quantity = request.form["quantity"]

        image = request.files["image"]
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO products(product_name, price, image, quantity)
            VALUES (%s, %s, %s, %s)
        """, (product_name, price, filename, quantity))

        mysql.connection.commit()
        cur.close()

        flash("Product Added Successfully!")
        return redirect("/index")

    return render_template("add_product.html")

@app.route('/admin_login',methods=['POST'])
def admin_login():
    
    username = request.form['username']
    password = request.form['password']
    if username == "" or password == "":
        flash("Please fill all fields", "danger")
        return redirect('/admin_login')
    cur = mysql.connection.cursor()
    cur.execute(
    "SELECT * FROM admin WHERE username=%s AND password=%s",
        (username, password)
    )
    
    user = cur.fetchone()
    cur.close()
    if user:
        flash("Login Successful!", "success")
        return render_template("admin_dashboard.html", username=username)
    else:
        flash("Invalid Username or Password!", "danger")
        return redirect('/')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if username == "" or password == "":
        flash("Please fill all fields", "danger")
        return redirect('/register')

    cur = mysql.connection.cursor()

    cur.execute(
        "INSERT INTO lgn(username,password) VALUES(%s,%s)",
        (username, password)
    )

    mysql.connection.commit()
    cur.close()

    flash("Registration Successful! Please Login.", "success")

    return redirect('/')



@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    if username == "" or password == "":
        flash("Please fill all fields", "danger")
        return redirect('/')

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM lgn WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cur.fetchone()
    cur.close()
    if user:
        flash("Login Successful!", "success")
        return redirect("/index")
    else:
        flash("Invalid Username or Password!", "danger")
        return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)