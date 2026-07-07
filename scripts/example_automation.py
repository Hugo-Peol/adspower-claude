"""Example: open an AdsPower profile and automate with Selenium."""

from adspower_client import open_profile, close_profile, list_profiles
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def automate_profile(user_id, url="https://www.google.com"):
    profile = open_profile(user_id)

    selenium_url = profile.get("ws", {}).get("selenium", "")
    webdriver_path = profile.get("webdriver", "")

    if not selenium_url or not webdriver_path:
        print("Could not get connection details. Is the profile open?")
        return

    options = Options()
    options.debugger_address = selenium_url

    service = Service(executable_path=webdriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        print(f"Page title: {driver.title}")
    finally:
        driver.quit()
        close_profile(user_id)


if __name__ == "__main__":
    profiles = list_profiles()
    if profiles:
        first_id = profiles[0].get("user_id")
        print(f"\nAutomating first profile: {first_id}")
        automate_profile(first_id)
    else:
        print("No profiles found. Create one first.")
