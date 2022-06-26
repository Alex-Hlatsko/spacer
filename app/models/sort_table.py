from flask import url_for, request
from flask_table import Table, Col

class sort_table(Table):
  id=Col("id")
  author=Col("Author")
  recommendation=Col("Recommendation")
  score=Col("Score")
  isPurchaseConfirmed=Col("Confirmed purchase")
  dateOpinionWritten=Col("Review date")
  dateProductBought=Col("Purchase date")
  votesYes=Col("Usefulness")
  votesNo = Col("Uselessness")
  content=Col("Content")
  upsides=Col("Upsides")
  downsides=Col("Downsides")
  allow_sort = True
  

  
  def sort_url(self, col_key, reverse=False):
    if reverse:
      direction = 'desc'
    else:
      direction = 'asc'
    return url_for(f"{request.endpoint}", **request.view_args,  sort_by=col_key, direction=direction)
  