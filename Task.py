import requests
from lxml import html
import json
from PIL import Image
import pytesseract
import requests
import urllib3

urllib3.disable_warnings()
self.session = requests.Session()
self.session.verify = False

class WebScraper:
    def __init__(self, tin_number):
        self.tin_number = tin_number
        self.url = "https://tinxsys.com/TinxsysInternetWeb/searchByTin_Inter.jsp"
        self.session = requests.Session()

    def get_captcha_image(self):
        response = self.session.get(self.url)
        tree = html.fromstring(response.content)
        captcha_img_url = tree.xpath("//img[@id='captchaImage']")[0].attrib['src']
        captcha_img_response = self.session.get(f"{self.url}/{captcha_img_url}")
        with open("captcha.png", "wb") as f:
            f.write(captcha_img_response.content)
        return "captcha.png"

    def solve_captcha(self, img_path):
        img = Image.open(img_path)
        captcha_text = pytesseract.image_to_string(img)
        return captcha_text.strip()

    def send_request(self, captcha_text):
        payload = {
            "tinNumber": self.tin_number,
            "captcha": captcha_text
        }
        response = self.session.post(self.url, data=payload)
        return response.content

    def parse_html(self, html_content):
        tree = html.fromstring(html_content)
        data = {
            "tin_number": self.tin_number,
            "cst_number": tree.xpath("//td[2]/text()")[0].strip(),
            "dealer_name": tree.xpath("//td[4]/text()")[0].strip(),
            "dealer_address": tree.xpath("//td[6]/text()")[0].strip(),
            "state_name": tree.xpath("//td[8]/text()")[0].strip(),
            "pan_number": tree.xpath("//td[10]/text()")[0].strip(),
            "registration_date": tree.xpath("//td[12]/text()")[0].strip(),
            "valid_upto": tree.xpath("//td[14]/text()")[0].strip(),
            "registration_status": tree.xpath("//td[16]/text()")[0].strip()
        }
        return data

    def scrape_data(self):
        img_path = self.get_captcha_image()
        captcha_text = self.solve_captcha(img_path)
        html_content = self.send_request(captcha_text)
        data = self.parse_html(html_content)
        return json.dumps(data, indent=4)

if __name__ == "__main__":
    tin_number = "21711100073"
    scraper = WebScraper(tin_number)
    print(scraper.scrape_data())