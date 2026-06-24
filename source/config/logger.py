from loguru import logger 
import sys 
 
def logger_settings(): 
   logger.remove() 
   logger.add( 
       sys.stdout, 
       format="{time:YYYY-MM-DD HH:mm:ss} | <level>{level:<8}</level> | <level>{message}</level>", 
       level="DEBUG", 
       colorize=True 
   ) 
   return logger 
 
logger = logger_settings()