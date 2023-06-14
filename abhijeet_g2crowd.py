import asyncio
import csv
import json
from playwright.async_api import async_playwright


async def scrape_company_details(url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()

        try:
            await page.goto(url)
            await page.wait_for_selector('div.product-card.x-ordered-events-initialized')

            elements = await page.query_selector_all('.product-card.x-ordered-events-initialized > *')

            data = []
            for element in elements:
                tag_name = await element.tag_name()

                if tag_name == 'img':
                    image_src = await element.get_attribute('src')
                    data.append({'type': 'image', 'src': image_src})
                else:
                    text_content = await element.text_content()
                    data.append({'type': 'text', 'content': text_content})

            return {
                'url': url,
                'data': data,
            }
       
        except Exception as e:
            print(f"An error occurred while scraping {url}: {str(e)}")
        finally:
            await browser.close()


async def scrape_company_details_from_csv(csv_file):
    results = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        urls = [row['url'] for row in reader]

    tasks = [scrape_company_details(url) for url in urls]
    results = await asyncio.gather(*tasks)

    return results


async def save_results_to_json(results, output_file):
    with open(output_file, 'w') as file:
        json.dump(results, file)


async def main():
    csv_file = 'g2crowd_urls.csv'
    output_file = 'company_details.json'

    results = await scrape_company_details_from_csv(csv_file)
    await save_results_to_json(results, output_file)


if __name__ == '__main__':
    asyncio.run(main())
