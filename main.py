import re
from os import makedirs
import argparse

from playwright.sync_api import sync_playwright

DEVICE_NAME = "2022 paperwhite"

parser = argparse.ArgumentParser()
parser.add_argument("--page", type=int, default=1, help="Page number to start from")
args = parser.parse_args()

start_url = f"https://www.amazon.co.uk/hz/mycd/digital-console/contentlist/booksPurchases/dateDsc?pageNumber={args.page}"

makedirs("downloads", exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.connect_over_cdp("http://localhost:9222")
    default_context = browser.contexts[0]
    page = default_context.new_page()
    page.goto(start_url)

    page.wait_for_selector("#CONTENT_LIST")

    # Get item count
    count_text = page.locator(".content-count").inner_text() # Showing 1 to 25 of 312 items
    item_count = int(match.group(1)) if (match := re.search(r'of (\d+) items', count_text)) else None

    # Get page count
    page_count = int(page.locator(".pagination .page-item:last-child").inner_text())

    print(f"Found {item_count} items across {page_count} pages")

    for page_index in range(args.page - 1, page_count):
        page_number = page_index + 1
        print(f"Processing page {page_number}/{page_count}")

        rows = page.locator("#CONTENT_LIST tbody tr").all()

        for index, row in enumerate(rows):

            title = row.locator(".digital_entity_title").inner_text()
            print(f"Downloading {index + 1}/{len(rows)}: {title}")

            row.locator(".dropdown_title").click()
            dropdown_menu = row.locator(".Dropdown-module_dropdown_container__2YGLm")
            download_button_matches = dropdown_menu.get_by_text("Download & transfer via USB") # dropdown menu contains modal, which repeats this text

            if download_button_matches.count() == 0:
                print(f"***No download button found for {title}")
                continue

            download_button_matches.first.click() 

            modal = dropdown_menu.locator(".DeviceDialogBox-module_container__1WOqR")
            devices = modal.get_by_role("listitem")
            target_device = devices.filter(has_text=DEVICE_NAME)
            target_device_radio = target_device.locator(".RadioButton-module_radio__1k8O3")
            target_device_radio.click()

            with page.expect_download() as download_info:
                modal.get_by_text("Download", exact=True).click()

            download = download_info.value
            download.save_as(f"downloads/{download.suggested_filename}")
            print(f"Saved to {download.suggested_filename}")

            page.locator("#notification-close").click()

        if page_number < page_count:
            page.locator(".pagination .page-item.active + .page-item").click()
            page.wait_for_selector("#CONTENT_LIST")
