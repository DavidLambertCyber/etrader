


class Market:
  def __init__(self, session, base_url):
    self.session = session
    self.base_url = base_url
    self.url_quote_path = '/v1/market/quote/'
    self.response = None

  def __clear_response(self):
    self.response = None

  def get_quotes(self,symbols='GOOG,IBM',session_params={'detailFlag':'ALL'}): #max 25
    self.__clear_response()
    url = self.base_url+self.url_quote_path+symbols+'.json'
    response = self.session.get(url, header_auth=True, params=session_params)
    self.response = response
    return self.response


      
      
      
      