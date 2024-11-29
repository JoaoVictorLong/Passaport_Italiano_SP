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

import json
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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

COOKIES_PATH = 'auth/cookies.json'
LOCAL_STORAGE_PATH = 'auth/local_storage.json'
check = 'https://prenotami.esteri.it/UserArea'

#configuracao chrome
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
    wait = WebDriverWait(chrome,20)
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
    wait = WebDriverWait(chrome,20)
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
    # chrome.get(page_login)
    # sleep(stop_normal)
    chrome.find_element(By.ID, 'login-email').send_keys(username)
    chrome.find_element(By.ID, 'login-password').send_keys(password, Keys.ENTER)
    sleep(stop_normal)
    navigate_and_check(page_login, chrome)
    validantion_login()

def delete_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            delete_folder(file_path) if os.path.isdir(file_path) else os.remove(file_path)
        os.rmdir(folder_path)
  
def custom_wait(driver, timeout, condition_type, locator_tuple):
    wait = WebDriverWait(driver, timeout)
    return wait.until(condition_type(locator_tuple))
   
def navigate_and_check(probe_page, chrome):
    chrome.get(probe_page)
    sleep(4)
    if success(chrome): # return True if you are loggged in successfully independent of saving new cookies
        save_data_to_json(chrome.get_cookies(), COOKIES_PATH)
        save_data_to_json({key: chrome.execute_script(f"return window.localStorage.getItem('{key}');") for key in chrome.execute_script("return Object.keys(window.localStorage);")}, LOCAL_STORAGE_PATH)
        return True
    else: 
        return False

def success(chrome):
    try:
        eternal_wait(chrome, 15, EC.presence_of_element_located, (By.XPATH, '/html/body/main/section/div[2]/img'))
        return True
    except:
        return False

def eternal_wait(driver, timeout, condition_type, locator_tuple): # timeout is symbolic here since it is eternal loop
    while True:
        try:
            element = custom_wait(driver, timeout, condition_type, locator_tuple)
            return element
        except:
            print(f"\n\nWaiting for the element(s) {locator_tuple} to become {condition_type}…")
            sleep(1) # just to display a message
            continue

def load_data_from_json(path): return json.load(open(path, 'r'))
def save_data_to_json(data, path): os.makedirs(os.path.dirname(path), exist_ok=True); json.dump(data, open(path, 'w'))

def add_cookies(chrome, cookies): [chrome.add_cookie(cookie) for cookie in cookies]
def add_local_storage(chrome, local_storage): [chrome.execute_script(f"window.localStorage.setItem('{k}', '{v}');") for k, v in local_storage.items()]

def get_first_folder(path): return os.path.normpath(path).split(os.sep)[0] # for this to work, keep the cookies and localstorage in the same folder!

def cookies_func(browser):
    browser.get(page_login)
    #Check and create directory to save cookies
    if os.path.exists(COOKIES_PATH) and os.path.exists(LOCAL_STORAGE_PATH):
        add_cookies(browser,load_data_from_json(COOKIES_PATH))
        add_local_storage(browser, load_data_from_json(LOCAL_STORAGE_PATH))
        
        if navigate_and_check(check, browser): # just pick a first link to check if the cookies are OK
            print("Using cookies")
            return # it is OK, you are logged in
        else: # cookies outdated, delete them
            delete_folder(get_first_folder(COOKIES_PATH)) # please keep the cookies.json and local_storage.json in the same folder to clear them successfully (or delete the outdated session files manually)
    
    browser.get(page_login)
    sleep(3)
    login(username ,password)

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
    cookies_func(chrome)
    while loop_book != 1:
        try:
            loop_book()
        except KeyboardInterrupt:
            print("Programa parado pelo usuario!")
            log.stop_programm("Programa parado pelo usuario!")