"""
在mac上跑的版本
需要自行根据本机chrome版本下载chromedriver，放到项目目录下。
下载地址：https://chromedriver.chromium.org/downloads

在项目根目录下执行。
"""
import click
import pandas as pd
from loguru import logger
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

time_config = {
    'mate x3': {'Date': None, 'Time': '10:08'}
    # 'mate x3': {'Date': None, 'Time': '16:50'} # for debug
}


class JD:
    def __init__(self, start_time: pd.Timestamp = None):
        browser = webdriver.Chrome('./chromedriver_mac_arm64/chromedriver')
        browser.maximize_window()
        self.browser = browser
        if start_time is None:
            start_time = pd.Timestamp.now()
        self.start_time = start_time

    def _get_button(self, button_name):
        try:
            if button_name in ['全选']:
                return self.browser.find_element(By.CLASS_NAME, 'jdcheckbox')
            if button_name in ['提交订单']:
                return self.browser.find_element(By.ID, 'order-submit')
            else:
                return self.browser.find_element(By.LINK_TEXT, button_name)
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


def get_start_time(stuff) -> pd.Timestamp:
    config = time_config.get(stuff)
    assert config is not None, stuff
    date, time = config['Date'], config['Time']
    if date is None:
        date = pd.Timestamp.now().strftime('%F')
    t = pd.to_datetime(f'{date} {time}:00')
    if t < pd.Timestamp.now():
        # 今天已经过了，抢明天的
        t += pd.Timedelta(days=1)
    logger.info(f'{stuff}抢购时间：{t}')
    return t


@click.command()
@click.option('--stuff', default='mate x3')
def run(stuff):
    start_time = get_start_time(stuff)
    jd = JD(start_time)
    # 进入京东购物车
    jd.go_to_cart()
    # 这里会跳出浏览器，请扫码登录。必须人工操作。
    # 确保是扫码登录界面，不是输入账户密码
    jd.get_button('扫码登录').click()
    logger.info('等待扫码登录...')
    while jd.browser.title != '京东商城 - 购物车':
        logger.info(jd.browser.title)
        time.sleep(1)
    # 等待登录加载
    logger.info('登录成功！')
    ready_time = start_time - pd.Timedelta(minutes=1)
    while pd.Timestamp.now() < ready_time - pd.Timedelta(minutes=1):  # 提前1分钟进入准备
        logger.info('还未到准备时间，睡眠1分钟')
        time.sleep(60)
    select_button = jd.get_button('全选')
    # 找到全选按钮，点击
    while not select_button.is_selected():
        logger.info('尝试点击中：{}'.format(pd.Timestamp.now()))
        # 尝试点击全选按钮
        select_button.click()
    jd.get_button('去结算').click()
    logger.info('成功提交结算')
    jd.get_button('提交订单').click()
    logger.info('成功提交订单')
    # 结束后会自动关闭浏览器，这里还没研究如何取消自动
    time.sleep(100)


if __name__ == '__main__':
    run()
