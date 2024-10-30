import os
import shutil
import logging
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from datetime import datetime, timedelta
import re

# Configuration des couleurs ANSI
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

# Définir le répertoire de base comme le répertoire où est hébergé le script
base_directory = os.path.dirname(os.path.abspath(__file__))
current_year = datetime.now().year

# Configuration des logs : fichier + console
log_directory = os.path.join(base_directory, f"StatistiqueGespage/{current_year}/logs")
os.makedirs(log_directory, exist_ok=True)
log_file_path = os.path.join(log_directory, "download_gespage_report.log")

# Configurer le logger
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter personnalisé avec couleur pour le terminal
class ColorFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            record.msg = f"{GREEN}{record.msg}{RESET}"
        elif record.levelno >= logging.ERROR:
            record.msg = f"{RED}{record.msg}{RESET}"
        return super().format(record)

console_handler.setFormatter(ColorFormatter('%(message)s'))

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, console_handler]
)

def log_start_end(func):
    """Decorator to log the start and end of functions."""
    def wrapper(*args, **kwargs):
        logging.info(f"Début de l'exécution de la fonction '{func.__name__}'")
        result = func.__call__(*args, **kwargs)
        logging.info(f"Fin de l'exécution de la fonction '{func.__name__}'")
        return result
    return wrapper

# Helper function to get the first and last date of the previous month
def get_previous_month_dates():
    today = datetime.today()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
    return first_day_of_previous_month.strftime("%d/%m/%Y"), last_day_of_previous_month.strftime("%d/%m/%Y")

def load_credentials(config_path="config.json"):
    """Charge les identifiants et l'URL depuis un fichier JSON."""
    config_path = os.path.join(base_directory, config_path)
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
            return config.get("username"), config.get("password"), config.get("url")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Erreur lors du chargement de la configuration : {e}")
        raise

@log_start_end
def configure_browser():
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": os.path.join(base_directory, f"StatistiqueGespage/{current_year}"),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--safebrowsing-disable-download-protection")
    chrome_options.add_argument("safebrowsing-disable-extension-blacklist")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver_path = os.path.join(base_directory, "chromedriver-linux64", "chromedriver")
    if not os.access(driver_path, os.X_OK):
        os.chmod(driver_path, 0o755)  # Rendre exécutable si nécessaire
    
    # Utilisation de Service pour spécifier le chemin du driver
    service = Service(driver_path)
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info("Navigateur configuré et démarré avec succès.")
        return driver
    except Exception as e:
        logging.error("Erreur lors de la configuration du navigateur.")
        raise e

@log_start_end
def download_report(driver):
    try:
        # Charger les identifiants et l'URL depuis le fichier config.json
        username, password, url = load_credentials()
        if not username or not password or not url:
            logging.error("Informations de connexion manquantes dans config.json.")
            return

        logging.info("Accès à la page de connexion...")
        driver.get(url)

        logging.info("Remplissage du formulaire de connexion.")
        driver.find_element(By.ID, "login_form:j_username").send_keys(username)
        driver.find_element(By.ID, "login_form:j_password").send_keys(password)

        login_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "login_form:j_idt17")))
        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        time.sleep(1)
        login_button.click()
        logging.info("Connexion réussie.")

        logging.info("Accès à la page de génération du rapport.")
        driver.get(f"{url}/app/report/detail-report.xhtml")

        start_date, end_date = get_previous_month_dates()
        logging.info(f"Définition de la période du rapport : {start_date} - {end_date}")

        wait = WebDriverWait(driver, 20)
        start_date_input = wait.until(EC.visibility_of_element_located((By.ID, "main_frm:startDate_input")))
        end_date_input = wait.until(EC.visibility_of_element_located((By.ID, "main_frm:endDate_input")))

        driver.execute_script("arguments[0].value = '';", start_date_input)
        start_date_input.send_keys(start_date)
        driver.execute_script("arguments[0].value = '';", end_date_input)
        end_date_input.send_keys(end_date)

        wait.until(EC.element_to_be_clickable((By.ID, "main_frm:j_idt134"))).click()
        logging.info("Génération du rapport initiée.")

        time.sleep(10)

        documents_path = os.path.join(base_directory, f"StatistiqueGespage/{current_year}")
        file_to_send = max([os.path.join(documents_path, f) for f in os.listdir(documents_path)], key=os.path.getctime)
        logging.info(f"Fichier téléchargé avec succès : {file_to_send}")

        file_to_send = standardize_filename(file_to_send)
        logging.info(f"Nom de fichier standardisé : {file_to_send}")

        if os.path.exists(file_to_send):
            logging.info(f"Le fichier {file_to_send} est prêt.")
        else:
            logging.error(f"Le fichier {file_to_send} est introuvable.")
        
        return file_to_send
    except Exception as e:
        logging.error("Erreur lors du téléchargement du rapport.")
        raise e
    finally:
        driver.quit()
        logging.info("Navigateur fermé.")

def standardize_filename(file_path):
    standardized_name = re.sub(r' \(\d+\)', '', file_path)
    if standardized_name != file_path:
        os.rename(file_path, standardized_name)
    return standardized_name

if __name__ == "__main__":
    logging.info("Début du script de téléchargement.")
    try:
        driver = configure_browser()
        download_report(driver)
        logging.info("Script terminé avec succès.")
    except Exception as e:
        logging.error(f"Script échoué : {e}")

