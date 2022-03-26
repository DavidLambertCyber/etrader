import logging,sys,os

class Logger:
  def __init__(self,level: str = 'INFO'):
    self.level = level.upper()
    self.level_choice = ['DEBUG','INFO','WARNING','ERROR','CRITICAL']
    self.log = self.apply_settings()
  
  def apply_settings(self):
    # logger conf
    FORMAT = "%(asctime)s|%(levelname)s|%(message)s"
    FILENAME = str(sys.argv[0]).replace('.py','_py')+'_Logs.txt'
    logger = logging.getLogger('my_logger')
    logging.basicConfig(filename=FILENAME,format=FORMAT,datefmt="%Y-%m-%dT%H:%M:%S%z")
    if self.level not in self.level_choice:
      print('Error in Logger: incorrect level choose DEBUG|INFO|WARNING|ERROR|CRITICAL',file=sys.stderr,flush=True)
      sys.exit(-1)
    
    logger.setLevel(self.level)
    logger.info('Start: '+os.path.abspath(sys.argv[0]))
    return logger

  def info(self,message: str):
    self.log.info(message)
  
  def error(self,message: str):
    self.log.error(message)
    print(message,file=sys.stderr,flush=True)
    
  def warning(self,message: str):
    self.log.warning(message)
    
  def critical(self,message: str):
    self.log.critical(message)
    print(message,file=sys.stderr,flush=True)
  
  def debug(self,message: str):
    self.log.debug(message)
    # print('')
    # print(message,flush=True)
