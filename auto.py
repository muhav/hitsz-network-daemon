import json
import time
import base64
import warnings
import requests
import timework as tw
from random import randint
from Crypto.Cipher import AES
from selenium import webdriver, common

warnings.filterwarnings("ignore")


class Encrypt(object):
    def __init__(self, key):
        self.key = key

    @staticmethod
    def add_to_16(value):
        while len(value) % 16 != 0:
            value += '\0'
        return str.encode(value)

    def encrypt_oracle(self, texts):
        """AES + base64."""
        aes = AES.new(Encrypt.add_to_16(self.key), AES.MODE_ECB)
        encrypt_aes = aes.encrypt(Encrypt.add_to_16(texts))
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
        return encrypted_text

    def decrypt_oracle(self, texts):
        """Base64 + AES."""
        aes = AES.new(Encrypt.add_to_16(self.key), AES.MODE_ECB)
        base64_decrypted = base64.decodebytes(texts.encode(encoding='utf-8'))
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8')
        return decrypted_text


def get_user_info():
    try:
        with open("userinfo.json") as f_obj:
            [username_e, password_e] = json.load(f_obj)
            pwd = Encrypt('network_HITsz')
            username_d = pwd.decrypt_oracle(username_e).split('\x00')[0]
            password_d = pwd.decrypt_oracle(password_e).split('\x00')[0]
    except FileNotFoundError:
        print("\nYou only need to fill in once:")
        username_d = input("username -> ")
        password_d = input("password -> ")
        with open("userinfo.json", 'w') as f_obj:
            pwd = Encrypt('network_HITsz')
            username_e = pwd.encrypt_oracle(username_d)
            password_e = pwd.encrypt_oracle(password_d)
            json.dump([username_e, password_e], f_obj)
    return username_d, password_d


class NetworkMonitor(object):
    def __init__(self):
        self.sleep_time = 5
        self.sleep_time_min = 5
        self.sleep_time_max = 120
        self.test_url = "http://www.baidu.com"
        self.login_page = "http://10.248.98.2/srun_portal_pc?ac_id=1&theme=basic2"

    def connection_test(self, link=""):
        @tw.limit(2)
        def get(url):
            return requests.get(url)

        try:
            rc = get(link if link else self.test_url).status_code
        except tw.TimeError:
            rc = 500

        if rc == 200:
            self.sleep_time += randint(1, self.sleep_time)
            self.sleep_time = min(self.sleep_time, self.sleep_time_max)
        else:
            self.sleep_time = self.sleep_time_min

        return rc == 200


def log_in(master, username, password):
    browser = webdriver.Chrome()
    browser.minimize_window()
    browser.get(master.login_page)

    browser.find_element_by_id('username').send_keys(username)
    browser.find_element_by_id('password').send_keys(password)
    browser.find_element_by_id('login').click()

    for i in range(10):
        try:
            browser.find_element_by_id('logout')
            break
        except common.exceptions.NoSuchElementException:
            time.sleep(.5)

    browser.quit()


if __name__ == '__main__':
    user = get_user_info()
    daemon = NetworkMonitor()

    while True:
        ok = daemon.connection_test()
        print(f"[ {'---' if ok else 'XXX'} ]  @ {time.strftime('%m.%d, %H:%M:%S')}")

        if not ok and daemon.connection_test(daemon.login_page):
            log_in(daemon, *user)
        time.sleep(daemon.sleep_time)
