from app import app
from flask import render_template, redirect, url_for, request
import os
import json
import pandas as pd
from app.models.product import Product

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/extraction', methods=["POST", "GET"])
def extraction():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        product = Product(product_id)
        product.extract_name()
        if product.product_name:
            product.extract_opinions().calculate_stats().draw_charts()
            product.export_opinions()
            product.export_product()
        else:
            error = "Ups... coś poszło nie tak"
            return render_template("extraction.html", error=error)
        return redirect(url_for('product', product_id=product_id))
    else:
        return render_template("extraction.html")

@app.route('/product/<product_id>')
def product(product_id):
    product = Product(product_id)
    product.import_product()
    stats = product.stats_to_dict()
    opinions = product.opinions_to_df()
    s = open(f'app/opinions/{product_id}.json', encoding="utf8")
    data = json.load(s)
    return render_template("product.html", product_id=product_id, stats=stats, opinions=opinions, data=data)

@app.route('/products')
def products():
    products = [filename.split(".")[0] for filename in os.listdir("app/products")]
    a = []
    for product in products:
        with open(f'app/products/{product}.json') as f:
            a.append(json.load(f))
    return render_template("products.html", products=products, a = a)

@app.route('/about')
def about():
    return render_template("about.html")