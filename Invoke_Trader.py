import os,sys
from textwrap import indent
from etrade.etrade import ETrade
# Remove-Item .\Invoke_Trader_py_Logs.txt ;cls; py.exe .\Invoke_Trader.py

from pprint import pprint

def main():
  et = ETrade(verbose=False,key_type='SANDBOX')
  # et = ETrade(verbose=False,key_type='LIVE')
  # et.get_quotes('BBW,TWO,F,GE,APA,TWNK,TTWO,BYND,CAT,GOOG,IBM,MRO,ACB,IDEX,BNGO,SNAP,NURO,RCON,RIG,BAC,TSLA,CGC,NIO,QS,SPWR,NEO,KMI')
  pprint(et.get_quotes('BBW,TWO,F,GE'),indent=2)
  et.revoke_token()
  
  
if __name__ == "__main__":
    main()