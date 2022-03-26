import webbrowser
from rauth import OAuth1Service

class OAuth:
  def __init__(self,name,consumer_key,consumer_secret,request_token_url,
                    access_token_url,authorize_url,base_url):
    self.name = name
    self.consumer_key = consumer_key
    self.__consumer_secret = consumer_secret
    self.request_token_url = request_token_url
    self.access_token_url = access_token_url
    self.authorize_url = authorize_url
    self.base_url = base_url
    self.session = self.__apply_session()
    self.response = None
    self.__cleanup()
    
  def __apply_session(self):
    anOauth = OAuth1Service(name = self.name,
                            consumer_key = self.consumer_key,
                            consumer_secret = self.__consumer_secret,
                            request_token_url = self.request_token_url,
                            access_token_url = self.access_token_url,
                            authorize_url = self.authorize_url,
                            base_url = self.base_url)
    
    request_token, request_token_secret = anOauth.get_request_token(
      params={"oauth_callback": "oob", "format": "json"})
    
    authorize_url = anOauth.authorize_url.format(anOauth.consumer_key, request_token)
    webbrowser.open(authorize_url)
    text_code = input("Please accept agreement and enter text code from browser: ")
    
    session = anOauth.get_auth_session(request_token,
                                request_token_secret,
                                params={"oauth_verifier": text_code})
    return session
    
  def __cleanup(self):
    del self.__consumer_secret
  
  def __clear_response(self):
    self.response = None

  def revoke_token(self):
    self.__clear_response()
    url = self.base_url + "/oauth/revoke_access_token"
    response = self.session.get(url, header_auth=True)
    self.response = response
    return self.response

