from requests import post
import config
def send():
    post(config.notify_url, data='Horario Disponivel'.encode(encoding='utf-8'))