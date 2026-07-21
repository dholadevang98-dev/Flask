import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, flash
import pymysql


app = Flask(__name__)
UPLOAD_FOLDER = "static/images/products"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = os.getenv("SECRET_KEY", "secretkey123")

conn = pymysql.connect(
    host=os.getenv("MYSQL_HOST", "autorack.proxy.rlwy.net"),
    port=int(os.getenv("MYSQL_PORT", "41814")),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", "YFNJZHhTkOXgZiGcNrYnxzsQrIDXKmlH"),
    database=os.getenv("MYSQL_DB", "railway")
)


@app.route('/register')
def register_page():
    return render_template("register.html")
@app.route('/')
def login_page():
    return render_template("login.html")
@app.route('/admin_login')
def admin_page():
    return render_template("admin_login.html")
@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")


@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):

    cur = conn.cursor()
    cur.execute("SELECT * FROM cart WHERE product_id=%s",(id))
    item = cur.fetchone()

    if item:
        cur.execute("UPDATE cart SET quantity = quantity + 1 WHERE product_id=%s",
            (id,))
    else:
        cur.execute("INSERT INTO cart(product_id, quantity) VALUES(%s,%s)",
            (id,1))
    conn.commit()
    cur.close()

    return redirect("/cart")

@app.route("/cart")
def cart():
    cur = conn.cursor()

    cur.execute("""
    SELECT
    cart.id,
    products.product_name,
    products.price,
    products.image,
    cart.quantity
    FROM cart
    JOIN products
    ON cart.product_id = products.id
    """)

    product = cur.fetchall()
    cur.close()
    return render_template("cart.html",products=product)
@app.route('/search')
def search():
    q = request.args.get("q")

    cur = conn.cursor()
    cur.execute(
    "SELECT * FROM products WHERE product_name LIKE %s",
    ("%" + q + "%",))

    products = cur.fetchall()
    return render_template("index.html",products=products)

@app.route("/delete_product/<int:id>",methods=['GET'])
def delete_product(id):
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    flash("Product Deleted Succesfully....")
    return redirect("/view_product")
    
@app.route("/edit_product/<int:id>",methods=['GET','POST'])
def edit_product(id):
    
    cur = conn.cursor()
    if request.method == "GET":
        cur.execute("SELECT * FROM products WHERE id=%s",(id,))
        product = cur.fetchone()
        return render_template("edit_product.html",product=product)
        
        
    product_name = request.form["product_name"]
    quantity = request.form["quantity"]
    price = request.form["price"]

    image = request.files["image"]
    if image.filename != "":
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        cur.execute("""UPDATE products 
        SET product_name=%s,quantity=%s,price=%s,image=%s WHERE id=%s
        """, (product_name, quantity, price, filename, id))

    else:
        cur.execute("""UPDATE products SET product_name=%s,
        quantity=%s,price=%s WHERE id=%s""", 
        (product_name, quantity, price, id))

    conn.commit()
    cur.close()

    flash("Product Updated Successfully")
    return redirect("/view_product")
@app.route('/view_product')
def view_product():
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    return render_template("view_product.html",products=products)

@app.route('/index')
def welcome():
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()

    print(products)

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

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO products(product_name, price, image, quantity)
            VALUES (%s, %s, %s, %s)
        """, (product_name, price, filename, quantity))

        conn.commit()
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
    cur = conn.cursor()
    cur.execute(
    "SELECT * FROM admin WHERE username=%s AND password=%s",
        (username, password)
    )
    
    user = cur.fetchone()
    cur.close()
    if user:
        flash("Login Successful!", "success")
        return redirect("/admin_dashboard")
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

    cur = conn.cursor()

    cur.execute(
        "INSERT INTO lgn(username,password) VALUES(%s,%s)",
        (username, password)
    )

    conn.commit()
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

    cur = conn.cursor()

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