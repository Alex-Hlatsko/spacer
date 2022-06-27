from flask import Response, render_template, request, redirect, url_for, Response
from app import app
import json

from app.__init__ import CeneoProduct, db
from app.models.product import Product
from app.models.utils import InvalidIdError, ProductAlreadyInDatabase
from app.models.sort_table import sort_table

@app.route("/")
def index():
  return render_template('index.html')

@app.route('/error404')
def error404():
  error = request.args.get("error", None)
  return render_template('error.html', error=error)

@app.route("/extraction")
def extraction():
  error = request.args.get("error", None)
  return render_template('extraction.html', error=error)

@app.route("/extract", methods=["POST", "GET"])
def extract():
  if request.method == "POST":
    try:
      # - Product Id
      product_id = int(request.form['product_id'])
      if not product_id:
        raise InvalidIdError()
      if CeneoProduct.query.get(product_id):
        raise ProductAlreadyInDatabase()

      # - Product in Database  
      newProduct = Product(product_id)
      newProduct.extract_info()
      newCeneoProduct = CeneoProduct(id=product_id, name=newProduct.name, opinions=newProduct.get_opinions_json(), averageScore=newProduct.averageScore)
      db.session.add(newCeneoProduct)
      db.session.commit()
      return redirect(f"/product/{product_id}")

      # - Errors
    except InvalidIdError:
      return redirect(url_for('extraction', error="Invalid Product ID"))
    except ProductAlreadyInDatabase:
      return redirect(url_for('extraction', error="Already In Database"))
    except OverflowError:
      return redirect(url_for('extraction', error="Invalid product ID"))
    except: 
      return redirect(url_for('error404', error="Problems in Pushing to DataBase, Please Check Product Id"))
  else:
    return redirect("/extraction")
  
@app.route("/products")
def products():
  try:
    # - Get Items From Database
    productsFromDb = CeneoProduct.query.order_by(CeneoProduct.dateCreated).all()
    # - Get Info For All Products in Database
    productsInfos = []
    for productFromDb in productsFromDb:
      product = Product(productFromDb.id, productFromDb.name, productFromDb.averageScore)
      product.set_opinions_from_json(productFromDb.opinions)
      productsInfos.append(product.get_product_details())
    
    return render_template("products.html", productsInfos=productsInfos)
  except:
    return redirect(url_for('error404', error="There was an issue in loading products!"))
  
@app.route("/product/<id>")
def product(id):
  try:
    # - Get All Url Parameters
    sortColumn = request.args.get('sort_by')
    sortDirection = request.args.get("direction")
    filterText = request.args.get('filter')
    filterColumn = request.args.get("column")
    # - Search Product from Database And Create a Product Object
    dbProduct = CeneoProduct.query.get_or_404(id) 
    productToDisplay = Product(dbProduct.id, dbProduct.name, dbProduct.averageScore)
    productToDisplay.set_opinions_from_json(dbProduct.opinions)
    # - Sort And Filter The Opinions According To Url Arguments
    if sortColumn and sortDirection:
      productToDisplay.sort_opinions(sortColumn, sortDirection)
    elif filterText and filterColumn:
      productToDisplay.filter_opinions(filterColumn, filterText)
    # - Create a Sortable Table Object And Render Products
    productTable = sort_table(productToDisplay.opinions, sort_by=sortColumn,sort_reverse=False if sortDirection == 'asc' else True)
    return render_template('product.html', product=productToDisplay, table=productTable)
  except:
    return redirect(url_for('error404', error="There was an issue in loading product data!"))
  
@app.route('/download-json/<id>')
def downloadJson(id):
  try:
    product = CeneoProduct.query.get_or_404(id)
    return Response(product.opinions, mimetype="application/json", headers={'Content-Disposition':f'attachment;filename={id}.json'})
  except:
    return redirect(url_for('error404', error="Problems with downloading json!"))
    
@app.route("/download-csv/<id>")
def downloadCsv(id):
  try:
    product = CeneoProduct.query.get_or_404(id)
    opinionsCsv = Product.convert_json(product.opinions, "csv")
    return Response(opinionsCsv, headers={'Content-Disposition':f'attachment;filename={id}.csv'})
  except:
    return redirect(url_for('error404', error="Problems with downloading csv!"))
  
@app.route("/download-xlsx/<id>")
def downloadXlsx(id):
  try:
    product = CeneoProduct.query.get_or_404(id)
    opinionsXlsx = Product.convert_json(product.opinions, 'xlsx')
    return Response(opinionsXlsx, headers={'Content-Disposition':f'attachment;filename={id}.xlsx'})
  except:
    return redirect(url_for('error404', error="Problems with downloading xlsx!"))

@app.route("/delete/<id>")
def delete(id):
  try:
    productToDelete = CeneoProduct.query.get_or_404(id)
    db.session.delete(productToDelete)
    db.session.commit()
    return redirect("/products")
  except:
    return redirect(url_for('error404', error="There was an issue in deleting this product!"))

@app.route("/charts/<id>")
def charts(id):
  try:
    productFromDb = CeneoProduct.query.get_or_404(id)
    product = Product(productFromDb.id, productFromDb.name, productFromDb.averageScore)
    product.set_opinions_from_json(productFromDb.opinions)
    firstChartData = product.get_counted_column_values_dict('recommendation')
    secondChartData = product.get_counted_column_values_dict('score')
    
    return render_template('charts.html', product_id=product.id, firstChartData=json.dumps(firstChartData), secondChartData=json.dumps(secondChartData))
  except:
    return redirect(url_for('error404', error="Not found!"))
    
@app.route('/about')
def about():
  return render_template('about.html')