from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import re

class GazetteDownloader:
    def __init__(self, base_dir="gazette_archives"):
        self.base_dir = Path(base_dir)
        self.setup_directories()
        self.base_url = "https://www.gazzettaufficiale.it"

    def setup_directories(self):
        """Create necessary directory structure"""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {self.base_dir}")

    def parse_date(self, title_text):
        """Extract date from title text and return in YYMMDD format"""
        # Match pattern like "del DD-MM-YYYY"
        match = re.search(r'del (\d{2})-(\d{2})-(\d{4})', title_text)
        if match:
            day, month, year = match.groups()
            return f"{str(year)[-2:]}{month}{day}"
        return None

    def navigate_to_year(self, page, year):
        """Navigate to the search page and select the specified year"""
        search_url = "https://www.gazzettaufficiale.it/ricerca/pdf/foglio_ordinario2/2/0/0?reset=true"
        print(f"\nNavigating to search page: {search_url}")
        page.goto(search_url)
        page.wait_for_load_state('networkidle')

        print(f"Selecting year: {year}")
        page.select_option('#annoPubblicazione', str(year))

        print("Clicking search button...")
        page.click('input[name="cerca"][value="Cerca"]')
        page.wait_for_load_state('networkidle')
        print("Navigation complete")

    def download_year(self, year):
        """Download all gazettes for a specific year"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            try:
                # Navigate to the correct year
                self.navigate_to_year(page, year)
                time.sleep(2)  # Wait for page to stabilize

                # Find all gazette elements
                elements = page.locator('.elemento_mese').all()
                print(f"\nFound {len(elements)} total gazette entries")

                current_date = None
                date_count = {}  # Track number of editions per date

                # Process each gazette
                for i, element in enumerate(elements, 1):
                    try:
                        # Get the title text which contains the date
                        title = element.locator('.titolo_atto').inner_text().strip()
                        print(f"\nProcessing entry {i}/{len(elements)}: {title}")

                        # Extract date in YYMMDD format
                        date_str = self.parse_date(title)
                        if not date_str:
                            print(f"Could not parse date from: {title}")
                            continue

                        # Update counter for this date
                        if date_str not in date_count:
                            date_count[date_str] = 0
                        date_count[date_str] += 1

                        # Create filename with counter
                        filename = f"{date_str}-{date_count[date_str]}.pdf"
                        filepath = self.base_dir / filename

                        # Skip if already downloaded
                        if filepath.exists():
                            print(f"Skipping {filename}, already exists")
                            continue

                        # Find and click the download button
                        download_link = element.locator('a.download_pdf')

                        # Start download
                        with page.expect_download() as download_info:
                            download_link.click()
                            download = download_info.value
                            print(f"Saving to: {filepath}")
                            download.save_as(filepath)
                            print(f"Downloaded: {filepath}")

                        time.sleep(2)  # Wait between downloads

                    except Exception as e:
                        print(f"Error processing entry {i}: {e}")
                        continue

                print("\nDownload process complete")
                print(f"Total dates processed: {len(date_count)}")
                print(f"Total editions downloaded: {sum(date_count.values())}")

                input("Press Enter to close the browser...")

            except Exception as e:
                print(f"Error: {e}")
            finally:
                browser.close()

def main():
    downloader = GazetteDownloader()
    # Download all gazettes from 1948
    downloader.download_year(1948)

if __name__ == "__main__":
    main()