
import argparse
from selenium.webdriver.common.by import By

from browser_automation import BrowserManager, Node
from utils import Utility
from x import Setup as XSetup, Auto as XAuto

PROJECT_URL = "https://x.com/"
EXTENTION_URL = "chrome-extension://fcjoldoebodoljbljpnkdnfgnpdgbdcm/dist/index.html"
class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        self.X_Setup = XSetup(node, profile)
        
    def _run(self):
        self.X_Setup._run()
        self.node.new_tab(f'https://hunter.membit.ai/?code=KNUHFDDF', method="get", wait=1)
        Utility.wait_time(10)

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.X_Auto = XAuto(node, profile)
        self.profile_name = profile.get('profile_name')
        self.email = profile.get('email')
        self.pwd_email = profile.get('pwd_email')

    def check_login(self):
        span_els = self.node.find_all(By.CSS_SELECTOR, 'span')
        for span in span_els:
            if 'Eligible Posts'.lower() in span.text.lower():
                self.node.log(f'Đã login extension')
                return True

    def scroll(self, value: int = 10):
        self.node.switch_tab(f'{PROJECT_URL}')
        times = 0
        scroll_to = 0
        times_in_reload = 0
        while True:
            articles = self.node.find_all(By.TAG_NAME, 'article', wait=5)

            if not articles:
                return 

            if scroll_to >= len(articles)-1:
                scroll_to = len(articles)-1
            
            self.node.scroll_to(articles[scroll_to], wait=0)
            self.node.log(f'Đã cuộn lần {times}')
            scroll_to += 1
            times += 1
            times_in_reload += 1
            if times_in_reload > 20:
                self.node.reload_tab()
                scroll_to = 0
                times_in_reload = 0
            
            if times > value:
                break 
            
        return times

    def _run(self):
        if not self.X_Auto._run():
            self.node.snapshot(f'Chưa login X')
            return
        self.node.new_tab(f'{EXTENTION_URL}', method="get")
        if not self.check_login():
            self.node.snapshot(f'Chưa login Membit')
            return
        times = self.scroll(200) # Thay đổi số lần scroll tại đây
        self.node.switch_tab(f'{EXTENTION_URL}')
        self.node.snapshot(f'scroll {times} lần')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.read_data('profile_name', 'email', 'pwd_email')
    max_profiles = Utility.read_config('MAX_PROFLIES')
    max_profiles = max_profiles[0] if max_profiles else 4
    
    if not profiles:
        print("Không có dữ liệu để chạy")
        exit()

    browser_manager = BrowserManager(AutoHandlerClass=Auto, SetupHandlerClass=Setup)
    browser_manager.config_extension('Membit-Data-Hunters-*')
    browser_manager.run_terminal(
        profiles=profiles,
        max_concurrent_profiles=max_profiles,
        auto=args.auto,
        headless=args.headless,
        disable_gpu=args.disable_gpu,
        sys_chrome=True
    )