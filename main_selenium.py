from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
import zipfile

# Step 3.1: Define proxy information
proxy_host = "{proxy_host}"
proxy_port = "{proxy_port}"
proxy_username = "{proxy_username}"
proxy_password = "{proxy_password}"

proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}"

seleniumwire_options = {
    "proxy": {
        "http": proxy_url,
        "https": proxy_url
    }
}

# Step 3.2: Set up Selenium Chrome options
chrome_options = Options()
# Add proxy to Chrome

# Create a Chrome extension with proxy authentication

# Create the proxy auth extension
#create_proxy_auth_extension(proxy_host, proxy_port, proxy_username, proxy_password)

# Set up Chrome options
# options = webdriver.ChromeOptions()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the page
driver.get("https://www.trustpilot.com/review/thesocialproxy.com")


def scroll_to_element(element):
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()


def close_cookie_banner():
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        cookie_button.click()
        print("Cookie banner closed")
    except (NoSuchElementException, TimeoutException):
        print("No cookie banner found or unable to close it")


def click_next_page():
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "pagination-button-next"))
        )
        scroll_to_element(next_button)
        try:
            next_button.click()
        except ElementClickInterceptedException:
            # If normal click fails, try using JavaScript
            driver.execute_script("arguments[0].click();", next_button)
        return True
    except (NoSuchElementException, TimeoutException):
        print("Next page button not found.")
        return False


with open('review_1.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Title", "Content", "Reviewer", "Date Posted", "Date of Experience", "Location"])

    def get_reviews():
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "styles_reviewsContainer__3_GQw")
            )
        )

        elements = driver.find_elements(By.CLASS_NAME, "styles_reviewCardInner__EwDq2")

        print(f"Number of reviews found: {len(elements)}")

        for el in elements:
            try:
                head = el.find_element(
                    By.CSS_SELECTOR,
                    ".typography_heading-s__f7029.typography_appearance-default__AAY17",
                )
                content = el.find_element(By.CLASS_NAME, "styles_reviewContent__0Q2Tg")
                reviewer = el.find_element(By.CLASS_NAME, "link_internal__7XN06")
                date_posted = el.find_element(By.CLASS_NAME, "styles_reviewHeader__iU9Px")


                print(f"Title: {head.text}")
                content_text = content.text
                reviewer_text = reviewer.text
                reviewer_text_array = reviewer_text.split('\n')
                content_text_array = content_text.split('\n')
                date_of_experience = content_text_array[-1]
                location = reviewer_text_array[-1]
                print(f"Content: {content.text}")
                print(f"Reviewer: {reviewer.text}")
                print(f"Date Posted: {date_posted.text}")
                print("------------------------------------------------------------------")

                # Write to CSV
                csv_writer.writerow([head.text, content.text, reviewer.text, date_posted.text, date_of_experience, location])  # Write data to CSV
            except (NoSuchElementException, StaleElementReferenceException) as e:
                print(f"Error extracting review details: {str(e)}")


    # Main scraping loop
    for i in range(3):
        print(f"PAGE NUMBER {i + 1}")

        get_reviews()

        if not click_next_page():
            print("No more pages to scrape.")
            break

        # Wait for the page to load after clicking next
        time.sleep(5)

# Close the browser
driver.quit()
