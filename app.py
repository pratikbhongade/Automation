import os
import time
import logging
import win32com.client as win32
import pythoncom
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException

# Set up logging
log_file_path = os.path.join(os.getcwd(), 'validation.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Prompt user to select the environment
environment = input("Please select the environment to be validated (IT, QV, Prod): ")

# Set the URL based on user input
if environment.lower() == "it":
    url = 'https://itintranet1.keybank.com/fpa/Login'
elif environment.lower() == "qv":
    url = 'https://qintranet1.keybank.com/fpa/Login'
elif environment.lower() == "prod":
    url = 'https://intranet1.keybank.com/fpa/Login'
else:
    raise ValueError("Invalid environment selected. Please choose 'IT', 'QV', or 'Prod'.")

logging.info(f"Selected environment: {environment}")

# Initialize Edge WebDriver
driver = webdriver.Edge()  # This will use the Edge WebDriver in your PATH

validation_results = []

# Function to highlight an element
def highlight(element):
    driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, "background: yellow; border: 2px solid red;")

# Function to check if a tab opens properly
def check_tab(tab_element, tab_name, content_locator, index):
    try:
        highlight(tab_element)
        time.sleep(1)  # Wait for 1 second before clicking the tab
        tab_element.click()
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located(content_locator))
        result = f"{index}. Main Tab '{tab_name}' opened successfully."
        print(result)
        logging.info(result)
        validation_results.append((result, "Success"))
        return True
    except TimeoutException:
        result = f"{index}. Failed to open Main Tab '{tab_name}'."
        print(result)
        logging.error(result)
        validation_results.append((result, "Failed"))
        return False

# Function to check if a sub-tab opens properly by executing JavaScript
def check_sub_tab(sub_tab_js, sub_tab_name, content_locator, main_index, sub_index):
    try:
        time.sleep(1)  # Wait for 1 second before clicking the sub-tab
        driver.execute_script(sub_tab_js)  # Execute JavaScript function directly
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located(content_locator))
        result = f"{main_index}.{chr(96+sub_index)}. Sub Tab '{sub_tab_name}' opened successfully."
        print(result)
        logging.info(result)
        validation_results.append((result, "Success"))
        return True
    except TimeoutException:
        result = f"{main_index}.{chr(96+sub_index)}. Failed to open Sub Tab '{sub_tab_name}'."
        print(result)
        logging.error(result)
        validation_results.append((result, "Failed"))
        return False
    except JavascriptException as e:
        result = f"{main_index}.{chr(96+sub_index)}. JavaScript error on Sub Tab '{sub_tab_name}': {e}"
        print(result)
        logging.error(result)
        validation_results.append((result, "Failed"))
        return False

# Function to validate the first list element under the specified column and click the cancel button
def validate_first_list_element_and_cancel(column_index, main_index, sub_index):
    try:
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.ListView")))
        rows = driver.find_elements(By.XPATH, f"//table[@class='ListView']/tbody/tr")
        if len(rows) <= 1:  # No data rows
            result = f"{main_index}.{chr(96+sub_index)}. There is no data in the sub tab '{sub_index}' to check so skipping."
            print(result)
            logging.info(result)
            validation_results.append((result, "Skipped"))
            return True

        try:
            first_element = driver.find_element(By.XPATH, f"//table[@class='ListView']/tbody/tr[2]/td[{column_index}]/a")
            highlight(first_element)
            time.sleep(1)  # Wait for 1 second before clicking the first element
            first_element.click()
            WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div#content")))

            # Wait for 1 second before clicking the cancel button
            time.sleep(1)

            # Find and click the cancel button (both jpg and gif)
            try:
                cancel_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "//img[contains(@src, '/fpa/images/btn_cancel.')]"))
                )
                highlight(cancel_button)
                time.sleep(1)  # Wait for 1 second before clicking the cancel button
                cancel_button.click()
                cancel_result = f"{main_index}.{chr(96+sub_index)}. Cancel button clicked successfully."
                print(cancel_result)
                logging.info(cancel_result)
                validation_results.append((cancel_result, "Success"))
            except (TimeoutException, NoSuchElementException) as e:
                cancel_result = f"{main_index}.{chr(96+sub_index)}. Failed to click the cancel button. Exception: {e}"
                print(cancel_result)
                logging.error(cancel_result)
                validation_results.append((cancel_result, "Failed"))

            return True
        except NoSuchElementException:
            result = f"{main_index}.{chr(96+sub_index)}. There is no first element in the sub tab '{sub_index}' to click so skipping."
            print(result)
            logging.info(result)
            validation_results.append((result, "Skipped"))
            return True
    except (TimeoutException, NoSuchElementException) as e:
        result = f"{main_index}.{chr(96+sub_index)}. Failed to open the first list element. Exception: {e}"
        print(result)
        logging.error(result)
        validation_results.append((result, "Failed"))
        return False

# Function to handle the "Search" sub-tab in "Check Mgmt."
def handle_search_sub_tab(main_index, sub_index):
    try:
        search_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//img[@src='/fpa/images/btn_search_bluebrdr.jpg']")))
        highlight(search_button)
        time.sleep(1)  # Wait for 1 second before clicking the Search button
        search_button.click()
        result = f"{main_index}.{chr(96+sub_index)}. Search button clicked successfully."
        print(result)
        logging.info(result)
        validation_results.append((result, "Success"))
        return True
    except (TimeoutException, NoSuchElementException) as e:
        result = f"{main_index}.{chr(96+sub_index)}. Failed to click the Search button. Exception: {e}"
        print(result)
        logging.error(result)
        validation_results.append((result, "Failed"))
        return False

# Navigate to the webpage containing the tabs
driver.get(url)  # Use the URL based on user input
logging.info(f"Navigated to {url}")

# Main tab elements and their corresponding content locators
main_tabs = {
    "Users": ("/fpa/Usr", (By.CSS_SELECTOR, "table.ListView")),
    "User Roles": ("/fpa/UsrRoles", (By.CSS_SELECTOR, "table.ListView")),
    "Accounts": ("/fpa/Acct", (By.CSS_SELECTOR, "table.ListView")),
    "GL/CC's": ("/fpa/GlCstCntr", (By.CSS_SELECTOR, "table.ListView")),
    "Printers": ("/fpa/Printer", (By.CSS_SELECTOR, "table.ListView")),
    "Misc. Lookups": ("/fpa/AdminMiscLookup", (By.CSS_SELECTOR, "table.ListView")),
    "Check Mgmt.": ("/fpa/CheckManagement", (By.CSS_SELECTOR, "table.ListView")),
    "Archive": ("/fpa/Archive", (By.CSS_SELECTOR, "table.ListView")),
    "Checks": ("/fpa/Check", (By.CSS_SELECTOR, "table.ListView")),
    "Payees": ("/fpa/Payee", (By.CSS_SELECTOR, "table.ListView")),
    "Tax Batch": ("/fpa/Checkbatch", (By.CSS_SELECTOR, "table.ListView")),
    "Positive Pay": ("/fpa/ExportPositivePay", (By.CSS_SELECTOR, "table.ListView")),
    "Export": ("/fpa/ExportGl", (By.CSS_SELECTOR, "table.ListView")),
    "Reconcile": ("/fpa/Reconcile", (By.CSS_SELECTOR, "table.ListView")),
}

# Sub-tabs for different main tabs and their corresponding content locators
sub_tabs_map = {
    "Users": {
        "Active": ("showList('Active', 'Usr');", (By.ID, "content")),
        "Not Active": ("showListNew('InActive', 'Usr');", (By.ID, "content")),
        "All": ("showListNew('All', 'Usr');", (By.ID, "content")),
    },
    "User Roles": {
        "Active": ("showList('Active', 'UsrRoles');", (By.ID, "content")),
        "Not Active": ("showListNew('InActive', 'UsrRoles');", (By.ID, "content")),
        "All": ("showListNew('All', 'UsrRoles');", (By.ID, "content")),
    },
    "Accounts": {
        "Active": ("showList('Active', 'Acct');", (By.ID, "content")),
        "Not Active": ("showListNew('InActive', 'Acct');", (By.ID, "content")),
        "All": ("showListNew('All', 'Acct');", (By.ID, "content")),
    },
    "GL/CC's": {
        "Active": ("showList('Active', 'GlCstCntr');", (By.ID, "content")),
        "Not Active": ("showListNew('InActive', 'GlCstCntr');", (By.ID, "content")),
        "All": ("showListNew('All', 'GlCstCntr');", (By.ID, "content")),
    },
    "Printers": {
        "Active": ("showList('Active', 'Printer');", (By.ID, "content")),
        "Not Active": ("showListNew('InActive', 'Printer');", (By.ID, "content")),
        "All": ("showListNew('All', 'Printer');", (By.ID, "content")),
    },
    "Misc. Lookups": {
        "Active": ("showList('Active', 'AdminMiscLookup');", (By.ID, "content")),
        "Not Active": ("showListNew('InActive', 'AdminMiscLookup');", (By.ID, "content")),
        "All": ("showListNew('All', 'AdminMiscLookup');", (By.ID, "content")),
    },
    "Check Mgmt.": {
        "History": ("showList('History', 'CheckManagement');", (By.ID, "content")),
        "Search": ("showList('Search', 'CheckManagement');", (By.ID, "content")),
    },
    "Checks": {
        "New Check": ("showList('NewCheck', 'Check');", (By.ID, "content")),
        "Requested": ("showListNew('Requested', 'Check');", (By.ID, "content")),
        "Checks To Approve": ("showListNew('ChecksToApprove', 'Check');", (By.ID, "content")),
        "Not Printed": ("showList('NotPrinted', 'Check');", (By.ID, "content")),
        "Queue": ("showListNew('Queue', 'Check');", (By.ID, "content")),
        "Printed": ("showListNew('Printed', 'Check');", (By.ID, "content")),
        "Search": ("showListNew('Search', 'Check');", (By.ID, "content")),
        "Reports": ("showListNew('CheckToApproveReport', 'Check');", (By.ID, "content")),
    },
    "Payees": {
        "Search": ("showList('Search', 'Payee');", (By.ID, "content")),
    },
    "Tax Batch": {
        "Checks To Approve": ("showList('ChecksToApprove', 'Checkbatch');", (By.ID, "content")),
        "Not Printed": ("showListNew('NotPrinted', 'Checkbatch');", (By.ID, "content")),
        "Queue": ("showListNew('Queue', 'Checkbatch');", (By.ID, "content")),
        "Printed": ("showListNew('Printed', 'Checkbatch');", (By.ID, "content")),
        "Import Control": ("window.location.href='/fpa/CheckBatchView';", (By.CSS_SELECTOR, "table.ListView")),
    },
    "Positive Pay": {
        "Not Exported": ("showList('NotExported', 'ExportPositivePay');", (By.ID, "content")),
        "Exported": ("showListNew('Exported', 'ExportPositivePay');", (By.ID, "content")),
        "Export Control": ("showListNew('Control', 'ExportPositivePay');", (By.ID, "content")),
    },
    "Export": {
        "General Ledger": ("window.location.href='/fpa/ExportGl';", (By.CSS_SELECTOR, "table.ListView")),
        "PTMS": ("window.location.href='/fpa/ExportPtms';", (By.CSS_SELECTOR, "table.ListView")),
    },
    "Reconcile": {
        "Not Reconciled": ("showList('NotReconciled', 'Reconcile');", (By.ID, "content")),
        "Reconciled": ("showListNew('Reconciled', 'Reconcile');", (By.ID, "content")),
        "Abandoned": ("showListNew('Abandoned', 'Reconcile');", (By.ID, "content")),
        "Search": ("showListNew('Search', 'Reconcile');", (By.ID, "content")),
        "Import Control": ("window.location.href='/fpa/ReconcileBatchView';", (By.CSS_SELECTOR, "table.ListView")),
    },
}

# Map of specific columns to be clicked for each main tab and sub-tab
column_indices = {
    "Users": 2,  # 2nd column for Users
    "User Roles": 2,  # 2nd column for User Roles
    "Accounts": 2,  # 2nd column for Accounts
    "GL/CC's": 3,  # 3rd column for GL/CC's
    "Printers": 2,  # 2nd column for Printers
    "Misc. Lookups": 2,  # 2nd column for Misc. Lookups
    "Check Mgmt.": 4,  # 4th column for Check Mgmt.
    "Checks": {
        "New Check": None,
        "Requested": 2,
        "Checks To Approve": 2,
        "Not Printed": 2,
        "Queue": 2,
        "Printed": 4,
        "Search": None,
        "Reports": 2,
    },
    "Payees": {
        "Search": None,
    },
    "Tax Batch": {
        "Checks To Approve": 2,
        "Not Printed": 2,
        "Queue": 2,
        "Printed": 4,
        "Import Control": 1,
    },
    "Positive Pay": {
        "Not Exported": 5,
        "Exported": 4,
        "Export Control": 1,
    },
    "Export": {
        "General Ledger": 5,
        "PTMS": 7,
    },
    "Reconcile": {
        "Not Reconciled": 5,
        "Reconciled": 4,
        "Abandoned": 5,
        "Search": None,
        "Import Control": 1,
    },
}

all_tabs_opened = True

# Function to handle sub-tabs based on main tab
def handle_sub_tabs(tab_name, sub_tabs, main_index):
    global all_tabs_opened
    sub_tab_results = []
    for sub_index, (sub_tab_name, (sub_tab_js, sub_content_locator)) in enumerate(sub_tabs.items(), start=1):
        sub_success = check_sub_tab(sub_tab_js, sub_tab_name, sub_content_locator, main_index, sub_index)
        if sub_success:
            column_index = column_indices.get(tab_name)
            if isinstance(column_index, dict):
                column_index = column_index.get(sub_tab_name)
            if column_index is not None:
                first_list_element_success = validate_first_list_element_and_cancel(column_index, main_index, sub_index)
                if not first_list_element_success:
                    all_tabs_opened = False
            else:
                result = f"{main_index}.{chr(96+sub_index)}. There is no data in the sub tab '{sub_tab_name}' to check so skipping."
                print(result)
                logging.info(result)
                validation_results.append((result, "Skipped"))
        else:
            all_tabs_opened = False

        if sub_success:
            result = f"{main_index}.{chr(96+sub_index)}. Sub Tab '{sub_tab_name}' opened successfully."
            sub_tab_results.append((result, "Success"))
        else:
            result = f"{main_index}.{chr(96+sub_index)}. Failed to open Sub Tab '{sub_tab_name}'."
            sub_tab_results.append((result, "Failed"))
    
    return sub_tab_results

# Check main tabs and their respective sub-tabs
for i, (tab_name, (tab_href, content_locator)) in enumerate(main_tabs.items(), start=1):
    try:
        # Find the main tab element using its href attribute
        tab_element = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@href='{tab_href}']"))
        )
        highlight(tab_element)
        time.sleep(1)  # Wait for 1 second before clicking the main tab
        success = check_tab(tab_element, tab_name, content_locator, i)
        if success:
            result = f"{i}. Main Tab '{tab_name}' opened successfully."
            print(result)
            logging.info(result)
            validation_results.append((result, "Success"))

            if tab_name in sub_tabs_map:
                sub_tab_results = handle_sub_tabs(tab_name, sub_tabs_map[tab_name], i)
                validation_results.extend(sub_tab_results)

        else:
            result = f"{i}. Failed to open Main Tab '{tab_name}'."
            print(result)
            logging.error(result)
            validation_results.append((result, "Failed"))
            all_tabs_opened = False

    except (TimeoutException, NoSuchElementException) as e:
        result = f"{i}. Main Tab '{tab_name}' not found or not clickable. Exception: {e}"
        print(result)
        logging.error(result)
        validation_results.append((result, "Failed"))
        all_tabs_opened = False

# Wait for 1 second before closing the browser
time.sleep(1)
# Close the browser
driver.quit()

# Print completion message if all tabs opened successfully
if all_tabs_opened:
    result = ("Validation completed successfully.", "Success")
    print(result[0])
    logging.info(result[0])
    validation_results.append(result)
else:
    result = ("Validation failed.", "Failed")
    print(result[0])
    logging.error(result[0])
    validation_results.append(result)

# Function to send email with validation results
def send_email(subject, validation_results):
    pythoncom.CoInitialize()
    email_body = (
        "<html>"
        "<body style='font-family: Arial, sans-serif;'>"
        "<p>Hi Team,</p>"
        "<p>Please find the validation result of <strong>FPA IT Application</strong>:</p>"
        "<pre style='font-size: 14px; color: #333;'>"
    )

    for result, status in validation_results:
        email_body += f"{result}\n"

    email_body += "</pre>"
    if all_tabs_opened:
        email_body += "<p style='font-size: 18px; color: green;'><strong>Validation Successful</strong></p>"
    else:
        email_body += "<p style='font-size: 18px; color: red;'><strong>Validation Failed</strong></p>"
    email_body += (
        "<p>Best regards,</p>"
        "<p><strong>Your Name</strong><br>"
        "Your Position<br>"
        "Your Contact Information</p>"
        "</body>"
        "</html>"
    )

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = 'Pratik_Bhongade@keybank.com'  # Replace with the recipient email addresses
    mail.Subject = subject
    mail.HTMLBody = email_body
    mail.Attachments.Add(log_file_path)  # Attach the log file
    mail.Send()
    pythoncom.CoUninitialize()

# Send the validation results via email
email_subject = f"Validation Results for {environment} Environment"
send_email(email_subject, validation_results)
