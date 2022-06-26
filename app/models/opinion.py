class Opinion():
  def __init__(self, id, author, recommendation, score, isPurchaseConfirmed, dateOpinionWritten, dateProductBought, votesYes, votesNo, content, upsides, downsides):
    self.id = id
    self.author = author
    self.recommendation = recommendation
    self.score = score
    self.isPurchaseConfirmed = isPurchaseConfirmed
    self.dateOpinionWritten = dateOpinionWritten
    self.dateProductBought = dateProductBought
    self.votesYes = votesYes
    self.votesNo = votesNo
    self.content = content
    self.upsides = upsides
    self.downsides = downsides
    
  def get_upsides_downsides(htmlOpinion):
    upsides = []
    downsides = []
    for featuresColumn in htmlOpinion.find_all("div", class_="review-feature__col"):
      if featuresColumn.find('div', class_="review-feature__title").text == "Zalety":
        for feature in  featuresColumn.find_all("div", class_="review-feature__item"):
          upsides.append(feature.text)
      elif featuresColumn.find('div', class_="review-feature__title").text == "Wady":
         for feature in  featuresColumn.find_all("div", class_="review-feature__item"):
          downsides.append(feature.text)
    return {
      "upsides": upsides,
      "downsides": downsides
    }

    # If "Polecam" - Return "Positive" Else "Negative" 
  def get_recommendation(htmlOpinion):
    if htmlOpinion.find('span', class_="user-post__author-recomendation") and htmlOpinion.find('span', class_="user-post__author-recomendation").text.replace("\n", "") == "Polecam":
        return "Positive"
    else:
        return "Negative"

  def get_dates(htmlOpinion):
    dateOpinionWritten = ""
    dateProductBought = ""
    if len(htmlOpinion.find("span", class_="user-post__published").find_all("time")) == 2:
      dateOpinionWritten = htmlOpinion.find("span", class_="user-post__published").find_all("time")[0]['datetime']
      dateProductBought = htmlOpinion.find("span", class_="user-post__published").find_all("time")[1]['datetime']
    elif len(htmlOpinion.find("span", class_="user-post__published").find_all("time")) == 1:
      dateOpinionWritten = htmlOpinion.find("span", class_="user-post__published").find_all("time")[0]['datetime']
    return {
      "dateOpinionWritten": dateOpinionWritten,
      "dateProductBought": dateProductBought
    }

  def get_score(htmlOpinion):
    return htmlOpinion.find("span", class_='user-post__score-count').text.split('/')[0].replace(',', '.')
    
  def parse_html_opinion(htmlOpinion):
    # - Get All Upsides and Downsides
    upsidesAndDownsides = Opinion.get_upsides_downsides(htmlOpinion)
    # - Get Recommendation
    recommendation = Opinion.get_recommendation(htmlOpinion)
    # - Get Review Date and Purchase Date
    dates = Opinion.get_dates(htmlOpinion)
    # - Get and Parse Score
    score = Opinion.get_score(htmlOpinion)
    opinion = {
      "id": htmlOpinion['data-entry-id'],
      "author": htmlOpinion.find("span", class_="user-post__author-name").text.replace("\n", ""),
      "recommendation": recommendation,
      "score": score,
      "isPurchaseConfirmed": "Yes" if htmlOpinion.find('div', class_="review-pz") else "No",
      "dateOpinionWritten": dates["dateOpinionWritten"],
      "dateProductBought": dates["dateProductBought"],
      "votesYes": htmlOpinion.find('button', class_="vote-yes")['data-total-vote'],
      "votesNo": htmlOpinion.find('button', class_="vote-no")['data-total-vote'],
      "content": htmlOpinion.find('div', class_="user-post__text").text,
      "upsides": (",").join(upsidesAndDownsides["upsides"]),
      "downsides": (",").join(upsidesAndDownsides["downsides"])
    }
    return opinion
    
  def get_opinion_dictionary(self):
    opinionDictionary = {
      "id": self.id,
      "author": self.author,
      "recommendation": self.recommendation,
      "score": self.score,
      "isPurchaseConfirmed": self.isPurchaseConfirmed,
      "dateOpinionWritten": self.dateOpinionWritten,
      "dateProductBought": self.dateProductBought,
      "votesYes": self.votesYes,
      "votesNo": self.votesNo,
      "content": self.content,
      "upsides": self.upsides,
      "downsides": self.downsides
    }
    return opinionDictionary