import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException

def validate_application(environment_key, config):
    url = config['environments'][environment_key]
    logging.info(f"Selected environment: {environment_key}")

    # Initialize Edge WebDriver
    driver = webdriver.Edge()  # This will use the Edge WebDriver in your PATH

    validation_results = []

    def highlight(element):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, "background: yellow; border: 2px solid red;")

    def check_tab(tab_element, tab_name, content_locator, index):
        try:
            highlight(tab_element)
            time.sleep(1)
            tab_element.click()
            locator_type = content_locator['type']
            locator_value = content_locator['value']
            if locator_type == 'css':
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, locator_value)))
            elif locator_type == 'id':
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.ID, locator_value)))
            result = f"{index}. Main Tab '{tab_name}' opened successfully."
            logging.info(result)
            validation_results.append((result, "Success"))
            return True
        except TimeoutException:
            result = f"{index}. Failed to open Main Tab '{tab_name}'."
            logging.error(result)
            validation_results.append((result, "Failed"))
            return False

    def check_sub_tab(sub_tab_js, sub_tab_name, content_locator, main_index, sub_index):
        try:
            time.sleep(1)
            driver.execute_script(sub_tab_js)
            locator_type = content_locator['type']
            locator_value = content_locator['value']
            if locator_type == 'css':
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, locator_value)))
            elif locator_type == 'id':
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.ID, locator_value)))
            result = f"{main_index}.{chr(96 + sub_index)}. Sub Tab '{sub_tab_name}' opened successfully."
            logging.info(result)
            validation_results.append((result, "Success"))
            return True
        except TimeoutException:
            result = f"{main_index}.{chr(96 + sub_index)}. Failed to open Sub Tab '{sub_tab_name}'."
            logging.error(result)
            validation_results.append((result, "Failed"))
            return False
        except JavascriptException as e:
            result = f"{main_index}.{chr(96 + sub_index)}. JavaScript error on Sub Tab '{sub_tab_name}': {e}"
            logging.error(result)
            validation_results.append((result, "Failed"))
            return False

    def validate_first_list_element_and_cancel(column_index, main_index, sub_index, is_export_control=False):
        try:
            WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.ListView")))
            rows = driver.find_elements(By.XPATH, f"//table[@class='ListView']/tbody/tr")
            if len(rows) <= 1:
                result = f"{main_index}.{chr(96 + sub_index)}. There is no data in the sub tab '{sub_index}' to check so skipping."
                logging.info(result)
                validation_results.append((result, "Skipped"))
                return True

            try:
                first_element = driver.find_element(By.XPATH, f"//table[@class='ListView']/tbody/tr[2]/td[{column_index}]/a")
                highlight(first_element)
                time.sleep(1)
                first_element.click()
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div#content")))

                time.sleep(1)

                if is_export_control:
                    cancel_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//img[@src='/fpa/images/btn_cancel.jpg']"))
                    )
                else:
                    cancel_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//img[@src='/fpa/images/btn_cancel.gif']"))
                    )
                highlight(cancel_button)
                time.sleep(1)
                cancel_button.click()

                return True
            except NoSuchElementException:
                result = f"{main_index}.{chr(96 + sub_index)}. There is no first element in the sub tab '{sub_index}' to click so skipping."
                logging.info(result)
                validation_results.append((result, "Skipped"))
                return True
        except (TimeoutException, NoSuchElementException) as e:
            result = f"{main_index}.{chr(96 + sub_index)}. Failed to open the first list element. Exception: {e}"
            logging.error(result)
            validation_results.append((result, "Failed"))
            return False

    all_tabs_opened = True

    def handle_sub_tabs(tab_name, sub_tabs, main_index):
        nonlocal all_tabs_opened
        sub_tab_results = []
        for sub_index, (sub_tab_name, sub_tab_data) in enumerate(sub_tabs.items(), start=1):
            sub_success = check_sub_tab(sub_tab_data['script'], sub_tab_name, sub_tab_data['content_locator'], main_index, sub_index)
            is_export_control = tab_name == "Positive Pay" and sub_tab_name == "Export Control"
            if sub_success:
                column_index = config['tabs'][tab_name]['column_index']
                if isinstance(column_index, dict):
                    column_index = column_index.get(sub_tab_name)
                if column_index is not None:
                    first_list_element_success = validate_first_list_element_and_cancel(column_index, main_index, sub_index, is_export_control=is_export_control)
                    if not first_list_element_success:
                        all_tabs_opened = False
                else:
                    result = f"{main_index}.{chr(96 + sub_index)}. There is no data in the sub tab '{sub_tab_name}' to check so skipping."
                    logging.info(result)
                    validation_results.append((result, "Skipped"))
            else:
                all_tabs_opened = False

            if sub_success:
                result = f"{main_index}.{chr(96 + sub_index)}. Sub Tab '{sub_tab_name}' opened successfully."
                sub_tab_results.append((result, "Success"))
            else:
                result = f"{main_index}.{chr(96 + sub_index)}. Failed to open Sub Tab '{sub_tab_name}'."
                sub_tab_results.append((result, "Failed"))

        return sub_tab_results

    for i, (tab_name, tab_data) in enumerate(config['tabs'].items(), start=1):
        try:
            tab_element = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[@href='{tab_data['url']}']"))
            )
            highlight(tab_element)
            time.sleep(1)
            success = check_tab(tab_element, tab_name, tab_data['content_locator'], i)
            if success:
                result = f"{i}. Main Tab '{tab_name}' opened successfully."
                logging.info(result)
                validation_results.append((result, "Success"))

                if 'sub_tabs' in tab_data:
                    sub_tab_results = handle_sub_tabs(tab_name, tab_data['sub_tabs'], i)
                    validation_results.extend(sub_tab_results)

            else:
                result = f"{i}. Failed to open Main Tab '{tab_name}'."
                logging.error(result)
                validation_results.append((result, "Failed"))
                all_tabs_opened = False

        except (TimeoutException, NoSuchElementException) as e:
            result = f"{i}. Main Tab '{tab_name}' not found or not clickable. Exception: {e}"
            logging.error(result)
            validation_results.append((result, "Failed"))
            all_tabs_opened = False

    time.sleep(1)
    driver.quit()

    if all_tabs_opened:
        result = ("Validation completed successfully.", "Success")
        logging.info(result[0])
        validation_results.append(result)
    else:
        result = ("Validation failed.", "Failed")
        logging.error(result[0])
        validation_results.append(result)

    return validation_results, all_tabs_opened
