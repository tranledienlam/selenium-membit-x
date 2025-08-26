
import argparse
from selenium.webdriver.common.by import By

from browser_automation import BrowserManager, Node
from utils import Utility

PROJECT_URL = "https://x.com/"

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        
    def _run(self):
        self.node.new_tab(f'{PROJECT_URL}', method="get")
        Utility.wait_time(10)

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.profile_name = profile.get('profile_name')
        self.email = profile.get('email')
        self.pwd_email = profile.get('pwd_email')

    def loaded(self):
        retries = 2
        for attempt in range(1, retries + 1):
            if self.node.find(By.CSS_SELECTOR, '[id="react-root"]'):
                self.node.log(f'Tab đã load thành công.')
                return True

            if attempt < retries:
                self.node.log("Reload tab và thử lại...")
                self.node.reload_tab()

        self.node.log("Tab load thất bại sau nhiều lần thử.")
        return False

    def check_login(self):
        if not self.loaded():
            return
        btns = self.node.find_all(By.TAG_NAME, 'button')
        need_login = False
        for btn in btns:
            if 'Sign up with Apple'.lower() in btn.text.lower():
                self.node.log(f'Cần đăng nhập X')
                need_login = True
                break
            elif btn.get_attribute('aria-label') == 'Account menu':
                if self.node.find_all(By.TAG_NAME, 'article'):
                    self.node.log(f'Đã đăng nhập X')
                    return True
                else:
                    self.node.log('Kiểm tra trạng thái đăng nhập bằng tay')
                break

        
        if need_login:
            pass
        
        return False

    def _run(self):
        self.node.new_tab(f'{PROJECT_URL}', method="get")
        if self.check_login():
            return True
        
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.read_data('profile_name', 'username', 'email', 'pwd_email')
    max_profiles = Utility.read_config('MAX_PROFLIES')
    max_profiles = max_profiles[0] if max_profiles else 4
    
    if not profiles:
        print("Không có dữ liệu để chạy")
        exit()

    browser_manager = BrowserManager(AutoHandlerClass=Auto, SetupHandlerClass=Setup)
    # browser_manager.config_extension('Membit-Data-Hunters-*')
    browser_manager.run_terminal(
        profiles=profiles,
        max_concurrent_profiles=max_profiles,
        auto=args.auto,
        headless=args.headless,
        disable_gpu=args.disable_gpu,
        sys_chrome=True
    )