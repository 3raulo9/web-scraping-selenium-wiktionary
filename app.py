from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

def setup_driver():
    options = Options()
    options.add_argument('--headless')  # Run headless Chrome
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver

def scrape_wiktionary(language, word):
    url = f'https://en.wiktionary.org/wiki/{word}'
    driver = setup_driver()
    driver.get(url)
    
    try:
        # Locate the language section header
        lang_header = driver.find_element(By.XPATH, f'//h2/span[@id="{language}"]/..')
        
        # Locate the Pronunciation section header within the language section
        pronunciation_header = lang_header.find_element(By.XPATH, 'following-sibling::h3[@id="Pronunciation_2"]')
        
        # Collect the content below the Pronunciation header
        pronunciation_content = []
        next_sibling = pronunciation_header.find_element(By.XPATH, 'following-sibling::*')
        while next_sibling.tag_name not in ['h2', 'h3']:
            pronunciation_content.append(next_sibling.get_attribute('innerHTML'))
            next_sibling = next_sibling.find_element(By.XPATH, 'following-sibling::*')
        
        driver.quit()
        return pronunciation_content
    except Exception as e:
        driver.quit()
        return str(e)

@app.route('/scrape', methods=['GET'])
def scrape():
    language = request.args.get('language')
    word = request.args.get('word')
    
    if not language or not word:
        return jsonify({"error": "Please provide both 'language' and 'word' parameters."}), 400
    
    result = scrape_wiktionary(language, word)
    
    return jsonify({"data": result})

if __name__ == '__main__':
    app.run(debug=True)
