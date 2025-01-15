import os
import sqlite3
import urllib.parse
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from utils import check_cbo_description

def check_establishment_SQL(value_to_check):
    """
    Verifies the eligibility of establishments associated to the role CLINICO and GENERALISTA.
    
    Arg: value_to_check (str): unique concatenated values of IBGE+CNES to verify.
    
    Return: ans (int):
        1 if the establishment is found in the valid database.
        0 if it is not valid.
        -1 if it is not found in any database, so it needs to be checked on the CNES website.
    """   
    # Calculate paths to database files relative to the script's location.
    base_dir = os.path.dirname(__file__)
    db1_path = os.path.join(base_dir, "..", "databases", "estab_202411_159_152.db")
    db2_path = os.path.join(base_dir, "..", "databases", "estabelecimentos_202411.db")
    
    try:
        # Connect to the first database.
        with sqlite3.connect(db1_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM serv159152 WHERE valor = ?", (value_to_check,))
            result = cursor.fetchone()
            if result[0] > 0:
                # If the establishment is found in the first database, it is valid.
                return 1
        
        # Connect to the second database.
        with sqlite3.connect(db2_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM tabela_dados WHERE CO_UNIDADE = ?", (value_to_check,))
            result = cursor.fetchone()
            if result[0] > 0:
                # If the establishment is found in the second database, it is invalid.
                return 0
        
        # If the establishment is not found in any database, it needs to be checked on the CNES website.
        return -1
    
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        return -1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return -1

def check_establishment(reader_csv): 
    """
    Verifies if the establishment meets the criteria (APS).

    Args:
        reader_csv (csv.DictReader): CSV file reader.

    Returns:
        valid_cnes (list): List of valid CNES which indicates the valid establishments.
    """
    unique_ibge_cnes = []
    unique_cnes = []
    unique_establishment_name = []
    valid_cnes = []
    
    # Create lists of unique establishments ibge, cnes values and names that need to be checked
    for line in reader_csv:
        try:
            cnes_value = line["CNES"]
            chs_amb_value = float(line["CHS AMB."])
            cbo_description = line["DESCRICAO CBO"]
            establishment_value = line["ESTABELECIMENTO"]
            ibge_value = line["IBGE"]
            concat_ibge_cnes = ibge_value + cnes_value
            if concat_ibge_cnes not in unique_ibge_cnes and chs_amb_value >= 20:
                if check_cbo_description(cbo_description, ["MEDICO", "CLINICO"]) or \
                   check_cbo_description(cbo_description, ["MEDICOS", "CLINICO"]) or \
                   check_cbo_description(cbo_description, ["MEDICO", "GENERALISTA"]):
                    unique_ibge_cnes.append(concat_ibge_cnes)
                    unique_cnes.append(cnes_value)
                    unique_establishment_name.append(establishment_value)
        except:
            pass
    
    for i in range(len(unique_ibge_cnes)):
        try:
            if unique_cnes[i] in valid_cnes:
                continue
            status = check_establishment_SQL(unique_ibge_cnes[i])
            if status == 1:
                valid_cnes.append(unique_cnes[i])
            elif status == -1:
                cnes = str(unique_cnes[i])
                establishment_name = str(unique_establishment_name[i])
                check_establishment_online(cnes, establishment_name, valid_cnes)
        except Exception as e:
            logging.warning(f"Error checking establishment: {e}")
            continue
    return valid_cnes

def check_establishment_online(cnes, establishment_name, valid_cnes):
    """
    Check the establishment on the CNES website.

    Args:
        cnes (str): CNES value.
        establishment_name (str): Establishment name.
        valid_cnes (list): List of valid CNES.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Attempt to find the establishment by CNES value
        if not open_cnes_page(driver, cnes):
            # If not found, attempt to find by establishment name
            cnes_encoded = urllib.parse.quote_plus(establishment_name)
            if not open_cnes_page(driver, cnes_encoded):
                logging.warning(f"The establishment {cnes} is not listed in CNES.")
                return
        
        # Navigate through the website to find the required information
        navigate_to_establishment_details(driver)
        check_services(driver, cnes, valid_cnes)
    finally:
        driver.quit()

def open_cnes_page(driver, search_value):
    """
    Open the CNES page for the given search value.

    Args:
        driver (webdriver): Selenium WebDriver instance.
        search_value (str): Search value (CNES or establishment name).

    Returns:
        bool: True if the page is opened successfully, False otherwise.
    """
    driver.get(f"https://cnes.datasus.gov.br/pages/estabelecimentos/consulta.jsp?search={search_value}")
    return wait_for_element(driver, "body > div.layout > main > div > div.col-md-12.ng-scope > div > div:nth-child(9) > table > tbody > tr > td:nth-child(8) > a > span", By.CSS_SELECTOR, 5)

def navigate_to_establishment_details(driver):
    """
    Navigate to the establishment details page.

    Args:
        driver (webdriver): Selenium WebDriver instance.
    """
    click_element(driver, "body > div.layout > main > div > div.col-md-12.ng-scope > div > div:nth-child(9) > table > tbody > tr > td:nth-child(8) > a > span")
    wait_for_element(driver, "Conjunto", By.LINK_TEXT, 5)
    click_element(driver, "Conjunto", by=By.LINK_TEXT)
    wait_for_element(driver, "#estabContent > aside > section > ul > li.treeview.active > ul > li:nth-child(1)", By.CSS_SELECTOR, 5)
    click_element(driver, "#estabContent > aside > section > ul > li.treeview.active > ul > li:nth-child(1)")
    wait_for_element(driver, "//table[@ng-table='tableParamsServicosEspecializados']", By.XPATH, 5)

def check_services(driver, cnes, valid_cnes):
    """
    Check the services provided by the establishment.

    Args:
        driver (webdriver): Selenium WebDriver instance.
        cnes (str): CNES value.
        valid_cnes (list): List of valid CNES.
    """
    rows = driver.find_elements(By.XPATH, "//table[@ng-table='tableParamsServicosEspecializados']//tbody//tr")
    for table_row in rows:
        code = table_row.find_element(By.XPATH, ".//td[@data-title-text='Código']").text
        if code == "159":
            valid_cnes.append(cnes)
            break
        elif code == "152":
            break

def wait_for_element(driver, selector, by, timeout):
    """
    Wait for an element to be present on the page.

    Args:
        driver (webdriver): Selenium WebDriver instance.
        selector (str): CSS selector or other selector.
        by (By): Type of selector.
        timeout (int): Timeout in seconds.

    Returns:
        bool: True if the element is found, False otherwise.
    """
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))
        return True
    except:
        return False

def click_element(driver, selector, by=By.CSS_SELECTOR):
    """
    Click on an element on the page.

    Args:
        driver (webdriver): Selenium WebDriver instance.
        selector (str): CSS selector or other selector.
        by (By): Type of selector.
    """
    element = driver.find_element(by, selector)
    element.click()


