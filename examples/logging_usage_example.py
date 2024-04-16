# myapp.py
import logging

logger = logging.getLogger(__name__)

def do_something():
    pass
def main():
    #logging.basicConfig(filename='myapp.log'""", level=logging.INFO)
    #logging.basicConfig(level=logging.INFO)
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    logger.debug('Started')
    do_something()
    logger.info('Finished')

if __name__ == '__main__':
    main()