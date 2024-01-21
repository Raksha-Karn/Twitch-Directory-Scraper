import json
from parsel import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_viewers_count(viewers_text):
    return viewers_text.strip()


options = Options()
options.headless = True
options.add_argument("--window-size=1920,1080")
options.add_argument("start-maximized")
options.add_argument("--incognito")
options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

driver = webdriver.Chrome(options=options)
driver.get("https://www.twitch.tv/directory")

main_page_data = []
sel_main = Selector(text=driver.page_source)

for item in sel_main.xpath("//div[contains(@class,'tw-tower')]/div[@data-target]"):
    main_page_data.append({
        'category': item.css('h2::text').get(),
        'url': item.css('.tw-link::attr(href)').get(),
        'viewers': item.css('.tw-link::text').get(),
        'tags': item.css('.tw-tag ::text').getall(),
    })


with open('categories_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(main_page_data, json_file, ensure_ascii=False, indent=4)

print("Main page data saved to categories_data.json")


live_channels = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-test-selector="browse-header-tab-live-channels"]'))
)
live_channels.click()

element = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-target="directory-first-item"]'))
)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


element = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-target="directory-game__card_container"]'))
)

sel_live = Selector(text=driver.page_source)
parsed_live = []

for item in sel_live.xpath("//div[@data-target='directory-game__card_container']"):
    title = item.css('h3::text').get()
    url = item.css('a[data-a-target="preview-card-channel-link"]::attr(href)').get()
    tags = item.css('.ScTagContent-sc-14s7ciu-1.VkjPH .ScTruncateText-sc-i3kjgq-0.ickTbV span::text').getall()
    viewers = extract_viewers_count(item.css('.tw-media-card-stat::text').get())

    parsed_live.append({
        'title': title,
        'user': url,
        'tags': tags,
        'viewers': viewers,
    })


with open('live_channels_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(parsed_live, json_file, ensure_ascii=False, indent=4)


print("Live channels data saved to live_channels_data.json")

driver.quit()
