from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse
from time import sleep
from datetime import datetime
import config
import log
from pyvirtualdisplay import Display

#Check machine
from platform import uname
system_version = uname()

stop_normal = 3
stop_longer = 100
#Variaveis padrões
username = config.username
password = config.password
page_login = "https://prenotami.esteri.it/"
page_book = 'https://prenotami.esteri.it/Services/Booking/2427'
frase_no_appointement = "Sorry, all appointments for this service are currently booked. Please check again tomorrow for cancellations or new appointments."

#configuracao browser
if system_version.machine == 'x86_64':
    print('Sistema Linux')
    options = Options()
    options.add_argument('--headless')
    options.add_experimental_option(
        "excludeSwitches", ['enable-automation'])

    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    options.add_argument("--remote-debugging-port=9222")
    chrome = Chrome(options=options)
else:
    #configuracao browser
    print('Sistema Rasp')
    display = Display(visible=0, size=(800,600))
    display.start()
    options = Options()
    options.add_argument('--headless')
    #options.add_experimental_option("excludeSwitches", ['enable-automation'])
    #options.add_experimental_option("useAutomationExtension", False)
    #options.add_argument("--disable-blink-features=AutomationControlled")                     
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    options.add_argument("--remote-debugging-port=9222")
    chrome = Chrome(service=Service(executable_path='/usr/bin/chromedriver'),options=options)
    #chrome.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


#Coleta de horas para execuao
def time():
    hora_atual = datetime.now()
    hora_atual_formatada = hora_atual.strftime('%d/%m/%y %T')
    return hora_atual_formatada

def validantion_login():
    try:
        check = chrome.find_element(By.TAG_NAME, 'body')
        if check.text == 'Unavailable':
            print("Acesso interompido pelo host. Tentando novamente em breve")
            log.page_stop("Acesso interompido pelo host. Tentando novamente em breve")
            sleep(200)
            login(username, password)
    except:
        None

#Login pagina Passaport
def login(user, passwd):
    chrome.get(page_login)
    sleep(stop_normal)
    chrome.find_element(By.ID, 'login-email').send_keys(username)
    chrome.find_element(By.ID, 'login-password').send_keys(password, Keys.ENTER)
    sleep(stop_normal)
    validantion_login()


def wait():
    sleep(stop_normal)
    validantion_login()
    try:
        check = chrome.find_element(By.XPATH, '//div[contains(@class, "jconfirm-content")]')
        return check
    except NoSuchElementException:
        sleep(stop_longer)
        volta_login = urlparse(chrome.current_url)
        if volta_login.query == 'ReturnUrl=%2fServices%2fBooking%2f2427':
            login(username, password)
        return 2
    except WebDriverException:
        print("Erro de conexão")
        log.page_stop("Erro de conexão")
        sleep(200)
        login(username, password)

#Loop books
def loop_book():
    chrome.get(page_book)
    sleep(stop_normal)
    if wait() == 2:
        print("Erro ao achar elemento:", time())
        sleep(stop_normal)
    else:
        check = chrome.find_element(By.XPATH, '//div[contains(@class, "jconfirm-content")]')
        if check.text == frase_no_appointement:
            print("Sem horario disponinvel", time())
            log.withoutbook("Sem horario disponinvel")
            sleep(stop_longer)
        else:
            print('\033[93mMUDANCA DE ROTINA!!!!\033[0m')
            log.found_book('MUDANCA DE ROTINA!!!!')
            return 1


if __name__ == '__main__':
    login(username, password)
    while loop_book != 1:
        try:
            loop_book()
        except KeyboardInterrupt:
            print("Programa parado pelo usuario!")
            log.stop_programm("Programa parado pelo usuario!")