import os
import shutil
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime, timedelta
from selenium.common.exceptions import StaleElementReferenceException

# Configuration des logs : fichier + console
log_directory = "/home/maheanuu/mes_scripts/export_gespage/logs"
os.makedirs(log_directory, exist_ok=True)
log_file_path = os.path.join(log_directory, "download_gespage_report.log")

# Configurer le logger
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(message)s'))

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
    
    start_date = first_day_of_previous_month.strftime("%d/%m/%Y")
    end_date = last_day_of_previous_month.strftime("%d/%m/%Y")
    
    return start_date, end_date

@log_start_end
def configure_browser(language_code="fr"):
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": f"/home/maheanuu/mes_scripts/export_gespage/{datetime.now().year}",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "intl.accept_languages": language_code  # Force la préférence linguistique
    })
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--lang={language_code}")  # Assure que Chrome s'affiche dans la langue souhaitée
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless=new")  # Active le mode headless
    chrome_options.add_argument("--user-data-dir=/tmp/chrome_profile")  # Utilise un profil temporaire

    driver_path = "/usr/local/bin/chromedriver"
    try:
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logging.info(f"Navigateur configuré et démarré avec succès en mode headless avec la langue '{language_code}'.")
        return driver
    except Exception as e:
        logging.exception("Erreur lors de la configuration du navigateur.")
        raise e

def retry_until_clickable(driver, by, value, retries=5, delay=1):
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((by, value)))
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            return element
        except (StaleElementReferenceException, Exception) as e:
            logging.warning(f"Tentative {attempt + 1} échouée pour localiser {value}. Erreur: {e}. Nouvel essai dans {delay} secondes...")
            time.sleep(delay)
    raise Exception(f"Impossible de localiser et interagir avec l'élément {value} après {retries} tentatives.")

def wait_for_download(directory, timeout=300):
    """Attend jusqu'à ce qu'un fichier complet apparaisse dans le répertoire spécifié."""
    logging.info("En attente de la fin du téléchargement...")
    end_time = time.time() + timeout
    while time.time() < end_time:
        for filename in os.listdir(directory):
            if filename.startswith(".") or filename.endswith(".crdownload"):  # Ignore les fichiers temporaires ou cachés
                continue
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                return file_path
        time.sleep(1)
    raise TimeoutError("Le téléchargement a pris trop de temps ou a échoué.")

@log_start_end
def download_report(driver):
    documents_path = f"/home/maheanuu/mes_scripts/export_gespage/{datetime.now().year}"
    try:
        logging.info("Accès à la page de connexion...")
        driver.get("http://192.168.203.37:7180/admin/")

        logging.info("Remplissage du formulaire de connexion.")
        driver.find_element(By.ID, "login_form:j_username").send_keys("admin")
        driver.find_element(By.ID, "login_form:j_password").send_keys("123456")

        login_button = retry_until_clickable(driver, By.ID, "login_form:j_idt17")
        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        time.sleep(1)
        login_button.click()
        logging.info("Connexion réussie.")

        logging.info("Accès à la page de génération du rapport.")
        driver.get("http://192.168.203.37:7180/admin/app/report/detail-report.xhtml")

        start_date, end_date = get_previous_month_dates()
        logging.info(f"Définition de la période du rapport : {start_date} - {end_date}")

        start_date_input = retry_until_clickable(driver, By.ID, "main_frm:startDate_input")
        driver.execute_script(f"document.getElementById('main_frm:startDate_input').value = '{start_date}';")
        start_date_input = driver.find_element(By.ID, "main_frm:startDate_input")
        start_date_input.send_keys(Keys.ENTER)

        end_date_input = retry_until_clickable(driver, By.ID, "main_frm:endDate_input")
        driver.execute_script(f"document.getElementById('main_frm:endDate_input').value = '{end_date}';")
        end_date_input = driver.find_element(By.ID, "main_frm:endDate_input")
        end_date_input.send_keys(Keys.ENTER)

        generate_button = retry_until_clickable(driver, By.ID, "main_frm:j_idt134")
        driver.execute_script("arguments[0].scrollIntoView(true);", generate_button)
        generate_button.click()
        logging.info("Génération du rapport initiée.")
        
        file_to_send = wait_for_download(documents_path)
        logging.info(f"Fichier téléchargé avec succès : {file_to_send}")

        return file_to_send
    except Exception as e:
        logging.exception("Erreur lors du téléchargement du rapport.")
        raise e
    finally:
        driver.quit()
        logging.info("Navigateur fermé.")

@log_start_end
def copy_file_to_new_location(file_to_send):
    year_folder = f"/home/maheanuu/mes_scripts/export_gespage/{datetime.now().year}/"
    try:
        new_file_path = os.path.join(year_folder, os.path.basename(file_to_send))
        if os.path.abspath(file_to_send) == os.path.abspath(new_file_path):
            logging.info(f"Le fichier est déjà à l'emplacement souhaité : {new_file_path}")
            return new_file_path

        shutil.copy(file_to_send, new_file_path)
        logging.info(f"Fichier copié avec succès vers : {new_file_path}")
        return new_file_path
    except Exception as e:
        logging.exception("Erreur lors de la copie du fichier vers le nouvel emplacement local.")
        raise e

if __name__ == "__main__":
    logging.info("Début du script de téléchargement.")
    language = "fr"  # Définir la langue ici, par exemple : "en", "fr", "es"
    try:
        driver = configure_browser(language_code=language)
        file_to_send = download_report(driver)
        copy_file_to_new_location(file_to_send)
        logging.info("Script terminé avec succès.")
    except Exception as e:
        logging.error(f"Script échoué : {e}")

