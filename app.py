from flask import Flask, render_template, request, send_from_directory
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    download_link = None
    error_message = None 
    if request.method == 'POST':
        keyword = request.form['keyword']
        location = request.form['location']
        num_pages = int(request.form.get('num_pages', 2)) 
        
        try:
            # Run the scraping function with the provided inputs
            output_file = run_scraping(keyword, location, num_pages)
            download_link = f"/download/{output_file}"
        except Exception as e:
            error_message = f"An error occurred: {str(e)}. Please check your inputs and try again."

    return render_template('index.html', download_link=download_link, error_message=error_message)

@app.route('/download/<filename>')
def download_file(filename):
    # Serve the file from the 'data' directory
    return send_from_directory('data', filename)

def run_scraping(keyword, location, num_pages):
    driver = webdriver.Chrome()
    driver.maximize_window()

    all_names = []
    all_links = []

    for page in range(1, num_pages + 1):
        start = (page - 1) * 10
        search_url = f"https://www.google.com/search?q=site%3Alinkedin.com%2Fin+%22{keyword}%22+%22{location}%22&start={start}"
        driver.get(search_url)
        time.sleep(2)

        # Extract names and profile URLs
        name_elements = driver.find_elements(By.XPATH, "//h3")
        for name_elem in name_elements:
            all_names.append(name_elem.text)

        link_elements = driver.find_elements(By.XPATH, "//a[@jsname='UWckNb']")
        for link in link_elements:
            url = link.get_attribute("href")
            all_links.append(url)

    driver.quit()

    # Save the data to an Excel file
    if len(all_names) != len(all_links):
        print(f"Warning: Mismatch in counts! Names: {len(all_names)}, URLs: {len(all_links)}")
        raise ValueError("Mismatch between names and links. Please try again.")
    
    # Check if no data was collected
    if not all_names or not all_links:
        raise ValueError("No results found. Please provide a proper keyword and location.")

    df = pd.DataFrame({
        'Name': all_names,
        'Profile URL': all_links
    })
    output_path = os.path.join('data', 'linkedin_profiles.xlsx')
    df.to_excel(output_path, index=False)
    print(f"Saved {len(all_names)} names and {len(all_links)} profile URLs to 'linkedin_profiles.xlsx'.")

    return 'linkedin_profiles.xlsx'

if __name__ == "__main__":
    app.run(debug=True)
