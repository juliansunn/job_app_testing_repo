from datetime import datetime
import requests
from bs4 import BeautifulSoup
from random import randint
from time import sleep

"""When you call the function get_jobs(pos, loc), you must include a position of interest (pos) and a location of interest (loc).  The location can be a city, state, or city and state.  It can include a comma as well.  The best practice would be to concatenate cities with states to make for a more uniform search.  When using this script, all you need to do is use the following command: from indeed_web_scrape import get_jobs.  

Once you call the get_jobs with a position and location, you will be returned a dictionary of jobs.  Each job will be referenced by a number and will contain a nested dictionary with the following keys: 'JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'Summary', 'Salary', 'JobUrl', 'JobDesc'.  The job description should be a list of lists with each nested list containing a paragraph or unique line of text based on the Indeed Job Summary. 
 
There is a sample.json file that will give an idea as to how the data is exactly packaged."""

# Create a template url with the position and location you are looking for
def get_url_and_headers(position, location):
    template = 'https://www.indeed.com/jobs?q={}&l={}'
    position = position.replace(' ', '+')
    location = location.replace(' ', '+')
    location = location.replace(",","%2C")
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47'
}
    url = template.format(position, location)
    return url, headers

# Get Job data from each record

def get_record(card):
    """Extract job data from a single record"""
    try:
        job_title = card.h2.span.get('title')
    except AttributeError:
        job_title = ""
    try:
        company = card.find('span', 'companyName').text.strip()
    except AttributeError:
        company = ""
    try:
        job_location = card.find('div', 'companyLocation').text
    except AttributeError:
        job_location = ""
    try:
        post_date = card.find('span', 'date').text
    except AttributeError:
        post_date = ""
    today = datetime.today().strftime('%Y-%m-%d')

    try:
        summary_list = card.find('div', 'job-snippet')
    except AttributeError:
        summary_list = ""
    summary = ""
    for li in summary_list.findAll('li'):
        summary+= li.text + ";"
    job_url = 'https://www.indeed.com' + card.a.get('href')
    # this does not exists for all jobs, so handle the exceptions
    try:
        salary = card.find('span', 'salary-snippet').text.strip()
    except AttributeError:
        salary = ''   
    record = [job_title, company, job_location, post_date, today, summary, salary, job_url]
    return record

# Run a while loop through all pages on the search site.  When there is no "Next" a tag, break return the results

def get_jobs(position, location):
    records = []
    url, headers = get_url_and_headers(position, location)
    while True:
        
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', 'mosaic-provider-jobcards')
        for card in cards:
            
            record = get_record(card)
            records.append(record)
            description = get_full_job_desc(record[-1])
            record.append(list(description))
            print('here')
        try:
            url = 'https://www.indeed.com' + soup.find('a', {'aria-label': 'Next'}).get('href')
            delay = randint(1, 5)
            sleep(delay)
        except AttributeError:
            break
    records_dict = {}
    columns=['JobTitle', 'Company', 'Location', 'PostDate', 'ExtractDate', 'Summary', 'Salary', 'JobUrl', 'JobDesc']
    for i, rec in enumerate(records):
        records_dict[i] = {}
        for j, c in enumerate(columns):
            records_dict[i][c] = rec[j]
    return records_dict


# Return the full job description from the job profile page

def get_full_job_desc(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    desc_div = soup.find('div', {'id': 'jobDescriptionText'})
    job_desc = ""
    if desc_div:
        for br in desc_div.find_all("br"):
            br.replace_with("\n")
        job_desc = desc_div.text.split("\n")
    return job_desc



