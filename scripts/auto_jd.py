import pandas as pd
from loguru import logger
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pyautogui


class JD:
    def __init__(self):
        browser = webdriver.Chrome('./chromedriver_win32/chromedriver.exe')
        browser.maximize_window()
        self.browser = browser

    def _get_button_by_class(self, class_):
        return self.browser.find_element(By.CLASS_NAME, class_)

    def _get_button_by_name(self, button_name):
        return self.browser.find_element(By.LINK_TEXT, button_name)

    def _get_button(self, button_name):
        try:
            if button_name in ['全选']:
                return self._get_button_by_class('jdcheckbox')
            else:
                return self._get_button_by_name(button_name)
        except NoSuchElementException:
            return

    def get_button(self, button_name):
        retry_times = 0

        while retry_times < 100:
            retry_times += 1
            button = self._get_button(button_name)
            if button is not None:
                return button
            else:
                logger.error(f'这个界面没有{button_name}按钮，重试次数{retry_times}，间隔0.1秒')
                # 向下滚200像素试试
                # self.browser.execute_script('window.scrollBy(0,200)')
                time.sleep(0.1)
        else:
            logger.error('重试超过100次！')
            raise NoSuchElementException(f'页面没有按钮：{button_name}')

    def go_to_cart(self):
        self.browser.get('https://cart.jd.com/')


if __name__ == '__main__':
    jd = JD()
    # 进入京东购物车
    jd.go_to_cart()
    # 这里会跳出浏览器，请扫码登录。必须人工操作。
    # 确保是扫码登录界面，不是输入账户密码
    jd.get_button('扫码登录').click()
    logger.info('请扫码')
    while jd.browser.title != '京东商城 - 购物车':
        logger.info(jd.browser.title)
        time.sleep(1)
    # 等待登录加载
    logger.info('登录成功！')
    select_button = jd.get_button('全选')
    # 找到全选按钮，点击
    while not select_button.is_selected():
        logger.info('尝试点击中：{}'.format(pd.Timestamp.now()))
        # 尝试点击全选按钮
        select_button.click()
    jd.get_button('去结算').click()
    # TODO 提交订单并不能正确点击，get不到
    jd.get_button('提交订单').click()
    # 结束后会自动关闭浏览器，这里还没研究如何取消自动
    time.sleep(100)
