from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
import time

# Initialize WebDriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Maximize browser window

driver = webdriver.Chrome(options=chrome_options)

admin_zbozi_url = "https://admin.zbozi.cz/"
sos_seznam_url = "https://sos.seznam.cz/"
user_email = "pavel.skultety@firma.seznam.cz"
user_name = "pavel.skultety"
user_password = "Salamyparkystavy1!"


def locate_element(driver, method, search_term, timeout=10):
    """Safely locates an element, handling exceptions."""
    try:
        locator_method = getattr(By, method)
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((locator_method, search_term))
        )
        if not element.is_displayed():
            raise Exception(f"Element {search_term} is not visible")
        return element
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error locating element {search_term}: {e}")
        return None


def login_to_admin_zbozi():
    driver.get(admin_zbozi_url)

    login_button = locate_element(driver, "XPATH", "//button[contains(text(), 'Přihlásit se') or contains(text(), 'Login')]")
    if login_button:
        login_button.click()

    user_email_input = locate_element(driver, "ID", "login-username")
    if user_email_input:
        user_email_input.clear()
        user_email_input.send_keys(user_email)

    user_email_submit_button = locate_element(driver, "XPATH", "//button[@data-locale='login.submit']")
    if user_email_submit_button:
        user_email_submit_button.click()

    username_input = locate_element(driver, "XPATH", "//input[@id='id_username']")
    password_input = locate_element(driver, "XPATH", "//input[@id='id_password']")
    
    if username_input and password_input:
        username_input.clear()
        username_input.send_keys(user_name)
        password_input.clear()
        password_input.send_keys(user_password)

        username_submit_button = locate_element(driver, "XPATH", "//input[@id='submit-button']")
        if username_submit_button:
            username_submit_button.click()

        token = input(f"Please enter the SMS token for {admin_zbozi_url}: ")
        token_input = locate_element(driver, "XPATH", "//input[@id='id_token']")
        if token_input:
            token_input.send_keys(token)

        remember_checkbox = locate_element(driver, "XPATH", "//input[@id='id_remember_device']")
        if remember_checkbox:
            remember_checkbox.click()

        submit_token = locate_element(driver, "XPATH", "//input[@id='submit-button']")
        if submit_token:
            submit_token.click()


def login_to_sos_seznam():
    driver.execute_script(f"window.open('{sos_seznam_url}', '_blank');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[1])  # Switch to new tab

    neznam_login_button = locate_element(driver, "XPATH", "//a[contains(@class, 'btn-secondary') and contains(@class, 'btn-block')]")
    if neznam_login_button:
        neznam_login_button.click()


def get_IC_number():
    """Fetch IC number from admin.zbozi.cz."""
    driver.switch_to.window(driver.window_handles[0])  # Switch to admin.zbozi.cz tab

    try:
        search_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, '_header__searchBtn_')]"))
        )
        
        print("Search icon found. Clicking...")
        search_icon.click()
        print("Search icon found. Clicked")

        #first_ic_element = WebDriverWait(driver, 10).until(
            #EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'IČ')]"))
        #)
        first_ic_element = locate_element(driver, "XPATH", "//span[contains(text(), 'IČ')]")
        IC_number = first_ic_element.text.split(":")[1].strip()
        print(f"Retrieved IC number: {IC_number}")
        return IC_number
    except Exception as e:
        print(f"Error getting IC number: {e}")
        return None


def add_new_ownership(IC_number):
    """Add new ownership in sos.seznam.cz."""
    driver.switch_to.window(driver.window_handles[1])  # Switch to sos.seznam.cz tab

    try:
        clients_menu_button = locate_element(driver, "XPATH", "//a[contains(text(), 'Klienti')]")
        if clients_menu_button:
            clients_menu_button.click()

        client_list_subitem = locate_element(driver, "XPATH", "//a[text()='Seznam klientů']")
        if client_list_subitem:
            client_list_subitem.click()

        ic_number_input = locate_element(driver, "ID", "clientFilter-ic")
        if ic_number_input:
            ic_number_input.clear()
            ic_number_input.send_keys(IC_number)
            ic_number_input.send_keys(Keys.RETURN)

        ic_number_link = locate_element(driver, "XPATH", f"//a[@href='/klient/{IC_number}' and text()='{IC_number}']")
        if ic_number_link:
            ic_number_link.click()

        ownership_link = locate_element(driver, "XPATH", "//a[text()='Vlastnictví']")
        if ownership_link:
            ownership_link.click()

        ownership_table = locate_element(driver, "XPATH", "//table[@id='ownership']")
        if ownership_table:
            print("Ownership table already exists. No action needed.")
            return

        print("Ownership table not found. Proceeding to add ownership...")

        add_owner_button = locate_element(driver, "XPATH", "//button[@id='add-item']")
        if add_owner_button:
            add_owner_button.click()

        add_owner_input = locate_element(driver, "XPATH", "//input[@name='whisperer-input-user_username_whisperer_popup']")
        if add_owner_input:
            add_owner_input.send_keys(user_name)

        add_owner_popup = locate_element(driver, "XPATH", "//div[@title='pavel.skultety' and contains(@class, 'whisperer-popup__column')]")
        if add_owner_popup:
            add_owner_popup.click()

        add_new_ownership_button = locate_element(driver, "XPATH", "//input[@name='add_new_ownership']")
        if add_new_ownership_button:
            add_new_ownership_button.click()

    except Exception as e:
        print(f"Error in add_new_ownership(): {e}")
        raise  # Rethrow the exception so monitor_ic_number() can handle it


def monitor_ic_number():
    """Continuously checks for new IC numbers and adds them."""
    last_ic_number = None
    while True:
        try:
            ic_number = get_IC_number()
            if ic_number and ic_number != last_ic_number:
                print(f"New IC number detected: {ic_number}")

                try:
                    add_new_ownership(ic_number)
                    last_ic_number = ic_number
                except Exception as e:
                    print(f"Error in add_new_ownership(): {e}")
                    print("Retrying IC number retrieval...")

        except Exception as e:
            print(f"Error in monitor_ic_number(): {e}")

        time.sleep(30)  # Adjust interval as needed


try:
    login_to_admin_zbozi()
    login_to_sos_seznam()
    monitor_ic_number()
except Exception as e:
    print("Fatal error:", e)
finally:
    driver.quit()
