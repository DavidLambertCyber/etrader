import os,sys,configparser,json,time
from etrade.logger.logger import Logger
from etrade.oauth.oauth import OAuth
from etrade.market.market import Market


REQUEST_TOKEN_URL="https://api.etrade.com/oauth/request_token"
ACCESS_TOKEN_URL="https://api.etrade.com/oauth/access_token"
AUTHORIZE_URL="https://us.etrade.com/e/t/etws/authorize?key={}&token={}"
RESTFUL_WAIT = 0.001

import pprint
PP = pprint.PrettyPrinter(indent=2)

#etrade handles combining various api, combine data, and logging

class ETrade:
  def __init__(self,key_type='SANDBOX',__config_file='CONFIG.ini',verbose=False):
    self.__config_file = __config_file
    self.key_type = key_type
    self.verbose = verbose
    self.__config = None
    self.log = None
    self.__oauth = None
    self.base_url = None
    self.response = None
    self.__apply_settings()
    self.session = self.__apply_session()
    self.market = self.__apply_market()

  def _convertStrCSV_toList(self,csvstr: str):
    return csvstr.split(',')

  def _convertList_toListOfLists(self,alist: list,maxlen: int = 25):
    #return list of lists
    cnt = 0
    subList = []
    alistOFLists = []
    if len(alist) < maxlen:
      alistOFLists.append(alist.copy())
      return alistOFLists

    for thing in alist:
      cnt += 1
      if cnt % maxlen == 0:
        alistOFLists.append(subList.copy())
        subList = []
      subList.append(thing)
      
    alistOFLists.append(subList.copy())
    return alistOFLists

  def _convertList_toStrCSV(self,alist: list):
    astr = ''
    for thing in alist:
      astr = astr+','+thing
    return astr

  def _convertResponseJSON_toDict(self,aresponse):
    if aresponse.ok:
      body = aresponse.text
      if '{' in body and 'html' not in body:
        aDict = json.loads(aresponse.content)
        return aDict
    return False

  def _convertResponseJSON_toStr(self,aresponse):
    aDict = self._convertResponseJSON_toDict(aresponse)
    if aDict is not False:
      JSONStr = json.dumps(aDict, indent=2, sort_keys=True)
      return JSONStr

    return False

  def __apply_settings(self):
    if not os.path.isfile(self.__config_file):
      print('Error:'+str(self.__config_file)+' file missing in working directory', file=sys.stderr, flush=True)
      sys.exit(-1)
    conf = configparser.ConfigParser()
    conf.read(self.__config_file)
    self.__config = conf
    log = Logger(self.__config['LOGS']['LOG_LEVEL'])
    self.log = log
    self.log.info(str(self.__config_file)+' processed')
    return True

  def __apply_session(self):
    global REQUEST_TOKEN_URL,ACCESS_TOKEN_URL,AUTHORIZE_URL
    self.base_url = self.__config[self.key_type]['BASE_URL']
    oa = OAuth( name='etrade',
                consumer_key = self.__config[self.key_type]['CONSUMER_KEY'],
                consumer_secret = self.__config[self.key_type]['CONSUMER_SECRET'],
                request_token_url = REQUEST_TOKEN_URL,
                access_token_url = ACCESS_TOKEN_URL,
                authorize_url = AUTHORIZE_URL,
                base_url = self.base_url )
    self.__oauth = oa
    return oa.session

  def __clear_response(self):
    self.response = None

  def __apply_market(self):
    m = Market(session=self.session, base_url=self.base_url)
    return m

  def __merge_get_quotes(self,DictList):
    finalDict = {}
    qd = []
    if len(DictList) == 1:
      finalDict = DictList[0]
      return finalDict
    #for aDict in DictList:
      #todo drill down to { 'QuoteResponse': { 'QuoteData': and get list to merge with qd
    
    return DictList
  
  def log_response_message(self,display_message: str = 'Info'):
    scs = ''
    body = ''
    if self.response is not None:
      #PP.pprint(self.response.text)#debug
      scs = str(self.response.status_code)
      body = self._convertResponseJSON_toStr(self.response)

      if self.response.ok:
        self.log.info(display_message+': '+self.response.reason+'| Status Code: '+scs)
        self.log.debug(display_message+' Request Headers: '+str(self.response.request.headers))
        self.log.debug(display_message+' Request URL: '+self.response.url)
        if body is not False:
          self.log.debug(display_message+' Response Body: '+body+'| Status Code: '+scs)
        if self.verbose:
          print(display_message+': '+self.response.reason+'\nStatus Code: '+scs,file=sys.stdout,flush=True)
        return True
      
      if not self.response.ok:
        self.log.error(display_message+': '+self.response.reason+'| Status Code: '+scs)
        self.log.debug(display_message+' Request Headers: '+str(self.response.request.headers))
        self.log.debug(display_message+' Request URL: '+self.response.url)
        if body is not False:
          self.log.debug(display_message+' Response Body: '+body)
        if self.verbose:
          print('Error: '+display_message+': '+self.response.reason+'\nStatus Code: '+str(scs),file=sys.stderr,flush=True)
        
        return True
    
    return False

  def revoke_token(self):
    self.__clear_response()
    response = self.__oauth.revoke_token()
    self.response = response
    self.log_response_message('revoke_token()')
    return self.response

  def get_quotes(self,symbols='GOOG,IBM',session_params={'detailFlag':'ALL'}):
    # returns array of quote response
    global RESTFUL_WAIT
    #todo working support more than 25 symbols by repeat calling market.get_quotes
    #split symbols by , to List, rebuild first 25, and so on.
    self.__clear_response()
    lSym = self._convertStrCSV_toList(symbols)
    llSym = self._convertList_toListOfLists(lSym)
    if llSym is None:
      self.log.error('get_quotes() Converting symbols to List of Lists fail, return None')
      if self.verbose:
        print('get_quotes() Converting symbols to List of Lists fail, return None')

    r = None
    ss = None
    rDict = None
    rDictList = []
    for someSymbols in llSym:
      ss = self._convertList_toStrCSV(someSymbols)
      r = self.market.get_quotes(ss,session_params=session_params)
      time.sleep(RESTFUL_WAIT)
      self.response = r
      self.log_response_message('get_quotes()')
      rDict = self._convertResponseJSON_toDict(r)
      if rDict is not None and 'QuoteResponse' in rDict and 'QuoteData' in rDict['QuoteResponse']:
        rDictList.append(rDict.copy())
      ss = None
      r = None
      rDict = None

    #finalDict = self.__merge_get_quotes(rDictList)
    #PP.pprint(finalDict)#debug
    #return finalDict
    return rDictList
      
    