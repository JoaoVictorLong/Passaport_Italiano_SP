import logging.handlers

#logging.basicConfig(level=logging.INFO, filename='appontment.log', format="%(asctime)s - %(levelname)s - %(message)s")
#Definindo um wait para o log achar novos arquivos

log_wait = logging.handlers.WatchedFileHandler('appontment.log')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.addHandler(log_wait)
logger.setLevel(logging.INFO)

def page_stop(messagem):
    logging.warning(messagem)

def withoutbook(messagem):
    logging.info(messagem)

def found_book(messagem):
    logging.info(messagem)

def stop_programm(messagem):
    logging.critical(messagem)