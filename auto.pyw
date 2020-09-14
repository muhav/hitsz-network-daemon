from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QKeySequence
from PyQt5.QtCore import pyqtSlot, Qt

import sys
import json
import time
import base64
import warnings
import requests
import threading
import timework as tw
from random import randint
from Crypto.Cipher import AES
from selenium import webdriver

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


class NetworkMonitor(object):
    def __init__(self):
        self.sleep_time = 3
        self.sleep_time_min = 3
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


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = '哈工深校园网守护'

        self.left = 360
        self.top = 240
        self.width = 300
        self.height = 350
        self.setFixedSize(self.width, self.height)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.setWindowIcon(QIcon('auto.ico'))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.shortcut.activated.connect(self.close)

        # self.statusBar().showMessage('Copyright. Lmh, Github: bugstop.')

        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)

        self.table_widget.countdown(daemon.sleep_time)

        self.show()

    def closeEvent(self, event):
        self.table_widget.label.setText('closed')  # stop countdown
        event.accept()  # let the window close
        # event.ignore()


class MyTableWidget(QWidget):

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        user_info = get_user_info()
        self.username = user_info[0]
        self.password = user_info[1]

        self.user = QPushButton(self)
        self.layout = QVBoxLayout(self)
        self.layout2 = QVBoxLayout(self)
        self.layout4 = QVBoxLayout(self)
        self.layout6 = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        # self.tabs.resize(300, 200)
        tab_font = QFont("Microsoft YaHei", 8, QFont.Normal)
        self.tabs.setFont(tab_font)

        # Add tabs
        self.tabs.addTab(self.tab1, "网络")
        self.tabs.addTab(self.tab2, "账户")

        self.set_tab_1()
        self.set_tab_2()

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def set_tab_1(self):
        # Create first tab
        f1 = QFont("Microsoft YaHei", 10, QFont.Light)
        f2 = QFont("Microsoft YaHei", 18, QFont.Normal)
        f3 = QFont("Consolas", 18, QFont.Light)

        self.tab1.layout = QVBoxLayout(self)

        self.horizontalGroupBox1 = QGroupBox("网络状态")
        self.horizontalGroupBox1.setFont(f1)
        self.horizontalGroupBox1.setStyleSheet("padding: 15px; border: 1px solid lightgray; border-radius: 0")
        layout = QGridLayout()
        layout.setSpacing(10)

        label1 = QLabel('互联网：', self)
        label1.setFont(f2)
        label1.setStyleSheet("padding: 0; border: 0; padding-right: 0;")
        label1.setAlignment(Qt.AlignLeft)
        layout.addWidget(label1, 1, 0, 1, 1)
        self.label2 = QLabel('尚未检测', self)
        self.label2.setFont(f2)
        self.label2.setStyleSheet("padding: 0; border: 0; padding-right: 0;")
        self.label2.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label2, 1, 1, 1, 1)

        label3 = QLabel('校园网：', self)
        label3.setFont(f2)
        label3.setStyleSheet("padding: 0; border: 0; padding-right: 0;")
        label3.setAlignment(Qt.AlignLeft)

        layout.addWidget(label3, 2, 0, 1, 1)
        self.label4 = QLabel('尚未检测', self)
        self.label4.setFont(f2)
        self.label4.setStyleSheet("padding: 0; border: 0; padding-right: 0;")
        self.label4.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label4, 2, 1, 1, 1)
        self.horizontalGroupBox1.setLayout(layout)
        self.tab1.layout.addWidget(self.horizontalGroupBox1)

        self.horizontalGroupBox3 = QGroupBox("检测间隔")
        self.horizontalGroupBox3.setFont(f1)
        self.horizontalGroupBox3.setStyleSheet("padding: 15px; border: 1px solid lightgray; border-radius: 0")
        cd = QGridLayout()
        cd.setSpacing(10)

        label5 = QLabel('当前间隔：', self)
        label5.setAlignment(Qt.AlignLeft)
        label5.setFont(f2)
        label5.setStyleSheet("padding: 0; padding-top: 10px; border: 0")
        label5.setAlignment(Qt.AlignLeft)
        cd.addWidget(label5, 1, 0, 1, 1)
        self.label6 = QLabel('0:20', self)
        self.label6.setAlignment(Qt.AlignLeft)
        self.label6.setFont(f3)
        self.label6.setStyleSheet("padding: 0; padding-top: 10px; border: 0")
        self.label6.setAlignment(Qt.AlignRight)
        cd.addWidget(self.label6, 1, 1, 1, 1)

        label7 = QLabel('下次检测：', self)
        label7.setAlignment(Qt.AlignLeft)
        label7.setFont(f2)
        label7.setStyleSheet("padding: 0; padding-top: 10px; border: 0")
        label7.setAlignment(Qt.AlignLeft)
        cd.addWidget(label7, 2, 0, 1, 1)
        self.label = QLabel('0:25', self)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setFont(f3)
        self.label.setStyleSheet("padding: 0; padding-top: 10px; border: 0")
        self.label.setAlignment(Qt.AlignRight)
        cd.addWidget(self.label, 2, 1, 1, 1)

        self.horizontalGroupBox3.setLayout(cd)
        self.tab1.layout.addWidget(self.horizontalGroupBox3)

        self.tab1.setLayout(self.tab1.layout)

    def countdown(self, remaining):
        if ":" not in self.label.text():
            return  # window closed
        while not self.password:
            reply = QMessageBox.information(self, '提示', '必须先绑定账号！',
                                            QMessageBox.Ok | QMessageBox.Close,
                                            QMessageBox.Close)
            if reply == QMessageBox.Ok:
                self.update_user_info()
            else:
                exit(0)

        if remaining > 0:
            self.label.setText('{}:{:02}'.format(*divmod(remaining, 60)))
            t = threading.Timer(1, self.countdown, (remaining - 1,))
            t.start()
        else:
            self.label.setText('{}:{:02}'.format(*divmod(remaining, 60)))

            ok1 = daemon.connection_test()
            ok2 = daemon.connection_test(daemon.login_page)

            if ok1:
                self.label2.setText('已连接上')
                self.label2.setStyleSheet("padding: 0; border: 0; padding-right: 0; color: green;")
            else:
                self.label2.setText('没有连接')
                self.label2.setStyleSheet("padding: 0; border: 0; padding-right: 0; color: red;")
            if ok2:
                self.label4.setText('已连接上')
                self.label4.setStyleSheet("padding: 0; border: 0; padding-right: 0; color: green;")
            else:
                self.label4.setText('没有连接')
                self.label4.setStyleSheet("padding: 0; border: 0; padding-right: 0; color: red;")

            if not ok1 and ok2 and not daemon.connection_test():
                log_in(daemon, self.username, self.password)
                daemon.sleep_time = 1

            self.label6.setText('{}:{:02}'.format(*divmod(daemon.sleep_time, 60)))
            t = threading.Timer(0, self.countdown, (daemon.sleep_time,))
            t.start()

    def set_tab_2(self):
        # Create first tab
        f1 = QFont("Microsoft YaHei", 10, QFont.Light)
        f2 = QFont("Microsoft YaHei", 18, QFont.Normal)
        f3 = QFont("Consolas", 15, QFont.Light)

        self.tab2.layout = QVBoxLayout(self)

        self.horizontalGroupBox = QGroupBox("账号绑定")
        self.horizontalGroupBox.setFont(f1)
        self.horizontalGroupBox.setStyleSheet("padding: 15px; border: 1px solid lightgray; border-radius: 0")

        user = QGridLayout()
        user.setSpacing(10)

        self.user.setText(self.username)
        self.user.clicked.connect(self.update_user_info)
        self.user.setFont(f2)
        self.user.setStyleSheet("padding: 0; border: 0; padding-right: 0; text-align: center;")
        user.addWidget(self.user, 1, 0, 1, 1)

        self.horizontalGroupBox.setLayout(user)
        self.tab2.layout.addWidget(self.horizontalGroupBox)

        self.horizontalGroupBox = QGroupBox("版权声明")
        self.horizontalGroupBox.setFont(f1)
        self.horizontalGroupBox.setStyleSheet("padding: 20px; border: 1px solid lightgray; border-radius: 0")
        copy = QGridLayout()
        copy.setSpacing(10)

        info1 = QLabel('Author:', self)
        info1.setFont(f3)
        info1.setStyleSheet("padding: 0; border: 0; padding-right: 0;")
        info1.setAlignment(Qt.AlignLeft)
        copy.addWidget(info1, 1, 0, 1, 1)

        info2 = QLabel('<a href="https://github.com/bugstop/schedule-shutdown-gui" '
                       'style="color: black !important; text-decoration: none">bugstop</a>', self)
        info2.setFont(f3)
        info2.setStyleSheet("padding: 0; border: 0; padding-right: 0;")
        info2.setAlignment(Qt.AlignRight)
        info2.setOpenExternalLinks(True)
        copy.addWidget(info2, 1, 1, 1, 1)

        info3 = QLabel('Licence:', self)
        info3.setFont(f3)
        info3.setStyleSheet("padding: 0; border: 0; padding-right: 0;")
        info3.setAlignment(Qt.AlignLeft)
        copy.addWidget(info3, 2, 0, 1, 1)

        info4 = QLabel('GPL 3.0', self)
        info4.setFont(f3)
        info4.setStyleSheet("padding: 0; border: 0; padding-right: 0;")
        info4.setAlignment(Qt.AlignRight)
        copy.addWidget(info4, 2, 1, 1, 1)

        self.horizontalGroupBox.setLayout(copy)
        self.tab2.layout.addWidget(self.horizontalGroupBox)

        self.horizontalGroupBox = QGroupBox("版本信息")
        self.horizontalGroupBox.setFont(f1)
        self.horizontalGroupBox.setStyleSheet("padding: 15px; border: 1px solid lightgray; border-radius: 0")
        info = QGridLayout()
        info.setSpacing(10)

        info5 = QLabel('Version:', self)
        info5.setFont(f3)
        info5.setStyleSheet("padding: 0; border: 0; padding-right: 0;")
        info5.setAlignment(Qt.AlignLeft)
        info.addWidget(info5, 1, 0, 1, 1)

        info6 = QLabel('2020.9.15', self)
        info6.setFont(f3)
        info6.setStyleSheet("padding: 0; border: 0; padding-right: 0;")
        info6.setAlignment(Qt.AlignRight)
        info.addWidget(info6, 1, 1, 1, 1)

        self.horizontalGroupBox.setLayout(info)
        self.tab2.layout.addWidget(self.horizontalGroupBox)

        self.tab2.setLayout(self.tab2.layout)

    @pyqtSlot()
    def update_user_info(self):
        while True:
            username_d, ok = QInputDialog().getText(QWidget(), '用户绑定', '输入账号：')
            if ok:
                self.username = username_d
                break
            elif self.password:
                return
            else:
                exit(0)

        while True:
            password_d, ok = QInputDialog().getText(QWidget(), '用户绑定', '输入密码：')
            if ok:
                self.password = password_d
                break

        with open("userinfo.json", 'w') as f_obj:
            pwd = Encrypt('network_HITsz')
            username_e = pwd.encrypt_oracle(username_d)
            password_e = pwd.encrypt_oracle(password_d)
            json.dump([username_e, password_e], f_obj)

        self.user.setText(username_d)
        return username_d, password_d


def get_user_info():
    try:
        with open("userinfo.json") as f_obj:
            [username_e, password_e] = json.load(f_obj)
            pwd = Encrypt('network_HITsz')
            username_d = pwd.decrypt_oracle(username_e).split('\x00')[0]
            password_d = pwd.decrypt_oracle(password_e).split('\x00')[0]
    except:
        username_d = '未绑定账号'
        password_d = ''
    return username_d, password_d


def log_in(master, username, password):
    browser = webdriver.Chrome()

    try:
        browser.minimize_window()
        browser.get(master.login_page)
        browser.find_element_by_id('username').send_keys(username)
        browser.find_element_by_id('password').send_keys(password)
        browser.find_element_by_id('login').click()
    except:
        pass

    for i in range(10):
        try:
            browser.find_element_by_id('logout')
            break
        except:
            time.sleep(.5)

    browser.quit()


if __name__ == '__main__':
    daemon = NetworkMonitor()
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
