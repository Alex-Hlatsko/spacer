from bs4 import BeautifulSoup
import requests, json, io
import pandas as pd

from app.models.opinion import Opinion
from app.models.utils import InvalidIdError

class Product():
  def __init__(self, id, name="", averageScore=0):
    self.id = id
    self.name = name
    self.opinions = []
    self.averageScore = averageScore

  # Get Product Name 
  def extract_name(product_page_soup):
    if product_page_soup.find("h1", class_="product-top__product-info__name"):
      return product_page_soup.find("h1", class_="product-top__product-info__name").text
    return ""
  
  # Get Product Score 
  def extract_score(product_page_soup):
    if product_page_soup.find("span", class_="product-review__score"):
      return float(product_page_soup.find("span", class_="product-review__score")['content'])
    return 0
  
  # Get Opinions PAGES
  def extract_opinions_pages(product_page_soup):
    opinions_count = int(product_page_soup.find('span', class_="product-review__qo").find('span').text)
    return opinions_count // 10 + 1 if opinions_count % 10 != 0 else opinions_count // 10

  # Get All Opinions On Pages
  def extract_opinions(opinionsPageSoup):
    # - Get HTML for Opinions On Current page
    htmlOpinions = opinionsPageSoup.find_all('div', class_="js_product-review")
    # - Parse HTML Opinions
    parsedOpinions = []
    for htmlOpinion in htmlOpinions:
      parsedOpinions.append(Opinion.parse_html_opinion(htmlOpinion))
    return parsedOpinions
    
  # Convert JSON format to CSV or XLSX
  def convert_json(jsonContent, dataFormat):
    df = pd.read_json(jsonContent)
    if dataFormat == "csv":
      return df.to_csv()
    elif dataFormat == "xlsx":
      output = io.BytesIO()
      df.to_excel(output)
      return output.getvalue()
    
  # Extracts All Product's Opinions
  def extract_info(self):
    # - Get HTML Code For Product Page
    product_page_soup = BeautifulSoup(requests.get(f'https://www.ceneo.pl/{self.id}').text, 'lxml')
    if product_page_soup.find('div', class_="error-page"):
      raise InvalidIdError("Invalid id!")
    self.name = Product.extract_name(product_page_soup)
    self.averageScore = Product.extract_score(product_page_soup)
    if product_page_soup.find('li', class_="reviews_new"):
      return
    opinionsPages = Product.extract_opinions_pages(product_page_soup)
    parsedOpinions = []
    for i in range(1, opinionsPages + 1):
      opinionsPageSoup = BeautifulSoup(requests.get(f'https://www.ceneo.pl/{self.id}/opinie-{i}').text, 'lxml')
      parsedOpinions += Product.extract_opinions(opinionsPageSoup)
    # - Create Opinion Objects And Add Them To Opinions Array
    for parsedOpinion in parsedOpinions:
      self.opinions.append(Opinion(*parsedOpinion.values()))
      

  # Returns Opinions As Dictionaries In A List
  def get_opinions_dictionary_list(self):
    opinions_dictionary_list = []
    for opinion in self.opinions:
      opinions_dictionary_list.append(opinion.get_opinion_dictionary())
    return opinions_dictionary_list

  # Return JSON-formatted Opinions
  def get_opinions_json(self):
    return json.dumps(self.get_opinions_dictionary_list(), indent=4)
  
  # Converts Opinions From JSON format to Opinion Object Format
  def set_opinions_from_json(self, jsonOpinions):
    opinions = []
    for opinion in json.loads(jsonOpinions):
      opinions.append(Opinion(*opinion.values()))
    self.opinions = opinions
    
  # Returns Products Details (id, name, average score, opinions' count, upsides and downisides count)
  def get_product_details(self):
    if self.opinions:
      
      df = pd.read_json(self.get_opinions_json())
      # - Count number of upsides
      upsidesCount = 0
      downsidesCount = 0
      for row in df['upsides']:
        if row:
          upsidesCount += len(row.split(','))
        
      # - Count number of downsides
      for row in df['downsides']:
        if row:
          downsidesCount += len(row.split(','))
            
      return {
        "id": self.id,
        "name": self.name,
        "averageScore": self.averageScore,
        "opinions_count": len(self.opinions),
        "upsidesCount": upsidesCount,
        "downsidesCount": downsidesCount
      }
    else:
      return {
        "id": self.id,
        "name": self.name,
        "averageScore": self.averageScore,
        "opinions_count": 0,
        "upsidesCount": 0,
        "downsidesCount": 0
      }
    
  # Sorts Opinions Depending On Column and Direction
  def sort_opinions(self, sortColumn, sortDirection):
    if(self.opinions):
      opinionsDf = pd.read_json(self.get_opinions_json())
      sortedOpinions = opinionsDf.sort_values(sortColumn, ascending = False if sortDirection == 'asc' else True ).to_json(orient='records')
      self.set_opinions_from_json(sortedOpinions)
    
  # Filters Opinions Depending On Column and Text
  def filter_opinions(self, filterColumn, filterText):
    if(self.opinions):
      opinionsDf = pd.read_json(self.get_opinions_json())
      filteredOpinions = opinionsDf.loc[opinionsDf[filterColumn].astype(str).str.contains(filterText)].to_json(orient='records')
      self.set_opinions_from_json(filteredOpinions)
    
  # Counts How Many Of Different Values There Are In Column - AND - Return Dictionary With Different Values As Keys And Their Count As Values
  def get_counted_column_values_dict(self, column):
     df = pd.read_json(self.get_opinions_json())
     return df[column].value_counts().to_dict()