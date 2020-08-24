import requests
import json
import winsound
import time
import base64
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
from multiprocessing import Process
import http.cookiejar as cookielib


class Selenium_Approach:
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.selenium_login()

    @classmethod
    def phantom_driver(cls):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap['phantomjs.page.settings.userAgent'] = (
            'Mozilla/5.0 (iPhone; CPU iPhone OS 8_1_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) CriOS/47.0.2526.70 Mobile/12B436 Safari/600.1.4 (000410)'
        )
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
        return driver

    def selenium_login(self):
        driver = self.phantom_driver()
        login_url = 'https://passport2.chaoxing.com/mlogin?loginType=1&newversion=true'
        driver.get(login_url)
        time.sleep(1)
        driver.find_element_by_id('phone').send_keys(self.user)
        driver.find_element_by_id('pwd').send_keys(self.password)
        driver.find_element_by_css_selector("[class='btn-big-blue margin-btm24']").click()
        time.sleep(5)
        cookies_list = driver.get_cookies()
        with open('PTLibCookies.json', 'w') as f:
            json.dump(cookies_list, f)

    def selenium_reserve(self, reserve_url, threshold, focus=None):
        driver = self.phantom_driver()
        count = 0
        stop = False
        while stop is False:
            print('第{}次查询……'.format(count))
            driver.get(reserve_url)
            driver.delete_all_cookies()
            with open('PTLibCookies.json', 'r') as f:
                cookie_list = json.load(f)
            for cookie in cookie_list:
                skip = 0
                for k, v in cookie.items():
                    if k == 'domain' and v != '.chaoxing.com':
                        skip = 1
                if skip == 1:
                    continue
                driver.add_cookie(cookie)
            driver.get(reserve_url)
            time.sleep(5)
            count += 1
            try:
                nweek0 = driver.find_element_by_class_name('th_week').text
                if '星期' in nweek0:
                    date = driver.find_elements_by_class_name('th_date')
                    infos = driver.find_elements_by_css_selector("[class='data_row']")
                    for i in range(len(infos)):
                        if focus is not None:
                            if date[i].text not in focus:
                                continue
                        info = infos[i]
                        reserve_nums = info.find_elements_by_css_selector("[class='td_num']")
                        time_loc = {0: '上午', 1: '下午'}
                        for e in range(len(reserve_nums)):
                            reserve_num = reserve_nums[e]
                            reserved = reserve_num.text.split('/')[0]
                            print(date[i].text, time_loc[e], ':', reserved)
                            if int(reserved) < threshold:
                                winsound.Beep(500, 3000)
                                stop = True
            except:
                continue
            time.sleep(30)


def parallel_reserve(user, password):
    selen_appro = Selenium_Approach(user, password)
    reserve_url1 = 'http://office.chaoxing.com/front/third/apps/reserve/item/reserve?itemId=2912&fidEnc=83ca4d93effeabde'
    p1 = Process(target=selen_appro.selenium_reserve, args=(reserve_url1, 70, ['08.25', ]))
    reserve_url2 = 'http://office.chaoxing.com/front/third/apps/reserve/item/reserve?itemId=2913&fidEnc=83ca4d93effeabde'
    p2 = Process(target=selen_appro.selenium_reserve, args=(reserve_url2, 30, ['08.25', ]))
    p1.start()
    p2.start()


class requests_service:
    def __init__(self, user, password):
        self.PTLibSession = requests.session()
        self.PTLibSession.cookies = cookielib.LWPCookieJar(filename="PTLibCookies.txt")
        self.header = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_1_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) CriOS/47.0.2526.70 Mobile/12B436 Safari/600.1.4 (000410)'
        }
        self.requests_login()

    def requests_login(self):
        encrypted_password = base64.b64encode(self.password.encode('utf-8'))
        login_url = 'https://passport2.chaoxing.com/fanyalogin'
        post_data = {
            'password': encrypted_password,
            'uname': self.user
        }
        response = requests.post(login_url, data=post_data, headers=self.header)
        # cookies = response.cookies.get_dict()
        self.PTLibSession.post(login_url, data=post_data, headers=self.header)
        self.PTLibSession.cookies.save()

    def reserve(self, reserve_url):
        self.PTLibSession.cookies.load()
        responseRes = self.PTLibSession.get(reserve_url, headers=self.header, allow_redirects=False)
        soup = BeautifulSoup(responseRes.text, 'html.parser')
        contents = soup.find_all(class_='td_info')
        for i in contents:
            print(i)


if __name__ == '__main__':
    user = '***'
    password = '***'
    parallel_reserve(user, password)
