import logging

logging.basicConfig(level=logging.INFO, filename='appontment.log', format="%(asctime)s - %(levelname)s - %(message)s")

def page_stop(messagem):
    logging.warning(messagem)

def withoutbook(messagem):
    logging.info(messagem)

def found_book(messagem):
    logging.info(messagem)

def stop_programm(messagem):
    logging.critical(messagem)