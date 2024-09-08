from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import subprocess
import re
from datetime import datetime

def get_router_mac_address(ip_address):
    try:
        # arpコマンドを実行して結果を取得
        result = subprocess.run(['arp', '-a', ip_address], capture_output=True, text=True)
        
        # MACアドレスを抽出
        mac_address = result.stdout.split('\n')[3].split()[1]
        
        return mac_address

    except Exception as e:
        print("Error occurred:", e)
    
    return None

def append_to_file(filename, data):
    with open(filename, 'a') as file:
        file.write(data + '\n')

ip_address = "192.168.11.1"
router_mac_address = get_router_mac_address(ip_address)
if router_mac_address:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_to_append = f"{current_time}: Router MAC Address for {ip_address}: {router_mac_address}"
    print(data_to_append)
    
    # ファイルにデータを追記
    append_to_file("router_mac_addresses.txt", data_to_append)
else:
    print(f"Router MAC Address for {ip_address} not found.")


print("WSR-1500AX2L FW アップデート & 自動設定スクリプト")
print("> adminのパスワードを入力してEnterキーを押下してください。")
password = input()

# FWのフルパスを入力
print("> このウインドウにファームウェアのファイルをドラッグアンドドロップしてEnterキーを押下してください。")
firmware_file_path = input()

# WebDriverの初期化（Chromeの場合）
driver_path = "./chromedriver.exe" # 実行ファイルと同じ階層にWebDriverのバイナリを配置
driver = webdriver.Chrome(service=ChromeService(driver_path))

driver.implicitly_wait(10)

# ルーターのIPアドレス
router_ip = "http://192.168.11.1"

# ログインページにアクセス
driver.get(router_ip)
driver.maximize_window()

# ログインフォームにユーザー名とパスワードを入力して送信
password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "form_PASSWORD")))
password_input.send_keys(password)
time.sleep(3)
driver.find_element(By.CLASS_NAME, "button_login").click()

# ログイン後、設定画面に移動
driver.get("http://192.168.11.1/advanced.html")

# EashMeshを無効化
driver.switch_to.default_content()
driver.find_element(By.CLASS_NAME, "WIRELESS").click()
driver.find_element(By.CLASS_NAME, "EASYMESH").click()
time.sleep(3)
driver.switch_to.frame("content_main")
if driver.find_element(By.ID, "easymesh_setting").is_selected():
  driver.find_element(By.ID, "easymesh_setting").click()
  driver.find_element(By.ID, "button_1").click()
  time.sleep(8)
WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.ID,"label_easymesh_warnning")))
driver.switch_to.default_content()

# WPA3 SSIDを無効化

## 2.4GHz
driver.switch_to.default_content()
driver.find_element(By.CLASS_NAME, "BAND2G").click()
time.sleep(5)
driver.switch_to.frame("content_main")
if driver.find_element(By.ID, "id_wpa3").is_selected():
  driver.find_element(By.ID, "id_wpa3").click()
  driver.find_element(By.ID, "button_1").click()
  time.sleep(10)

## 5.0GHz
driver.switch_to.default_content()
driver.find_element(By.CLASS_NAME, "BAND5G").click()
time.sleep(5)
driver.switch_to.frame("content_main")
if driver.find_element(By.ID, "id_wpa3").is_selected():
  driver.find_element(By.ID, "id_wpa3").click()
  driver.find_element(By.ID, "button_1").click()
  time.sleep(5)

# DHCPサーバーからの自動取得に変更
time.sleep(5)
driver.switch_to.default_content()
driver.find_element(By.CLASS_NAME, "WAN").click()
driver.find_element(By.CLASS_NAME, "CONNECT").click()
time.sleep(3)
driver.switch_to.frame("content_main")
driver.find_element(By.ID, "id_method2").click()
driver.find_element(By.ID, "button_1").click()
time.sleep(3)
WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.ID,"routeron")))
driver.switch_to.default_content()

# IPv6を無効化
driver.switch_to.default_content()
time.sleep(3)
driver.find_element(By.CLASS_NAME, "IPV6").click()
time.sleep(5)
driver.switch_to.frame("content_main")
time.sleep(5)
WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.ID,"basic_content")))
driver.find_element(By.ID, "method_disable").click()
driver.find_element(By.ID, "button_1").click()
time.sleep(5)
WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.ID,"basic_content")))
driver.switch_to.default_content()

# ファームウェアアップデート
driver.find_element(By.CLASS_NAME, "ADMIN").click()
driver.find_element(By.CLASS_NAME, "FIRMWARE").click()
time.sleep(3)
driver.switch_to.frame("content_main")
time.sleep(5)
driver.find_element(By.NAME, "file").send_keys(firmware_file_path)
time.sleep(10)
driver.find_element(By.NAME, "fwupbutton").click()

# WebDriverを終了
driver.quit()
