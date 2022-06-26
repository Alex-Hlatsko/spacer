from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

from app import routes

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ceneo_opinions.db'
db = SQLAlchemy(app)

class CeneoProduct(db.Model):
  id = db.Column(db.String(20), nullable=False, primary_key=True)
  name = db.Column(db.String(50), nullable=False)
  averageScore = db.Column(db.String(10))
  opinions = db.Column(db.String())
  dateCreated = db.Column(db.DateTime, default=datetime.utcnow)
  
  def __repr__(self):
    return "<CeneoProduct %r>" % self.id

if __name__ == "__main__":
  app.run(debug=True)