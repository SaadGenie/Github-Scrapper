import requests
from bs4 import BeautifulSoup
import pandas
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# for extracting encrypted emails
import re


# url = "https://www.umt.edu.pk/faculty.aspx"
# response = requests.get(url)
# page_content = response.text

# doc_parsing = BeautifulSoup(page_content , 'html.parser')

MAX_RETRIES = 5



# 7th function
def get_lecturer_page(lecturer_url):
	session = requests.Session()
	retries = Retry(total=MAX_RETRIES, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
	session.mount('http://', HTTPAdapter(max_retries=retries))
	session.mount('https://', HTTPAdapter(max_retries=retries))

	try:
		response = session.get(lecturer_url)
		response.raise_for_status()  # Raise HTTPError for bad requests
	except requests.exceptions.HTTPError as errh:
		print(f"HTTP Error occurred: {errh}")
		return None
	except requests.exceptions.ConnectionError as errc:
		print(f"Error Connecting: {errc}")
		return None
	except requests.exceptions.Timeout as errt:
		print(f"Timeout Error: {errt}")
		return None
	except requests.exceptions.RequestException as err:
		print(f"Something went wrong: {err}")
		return None
	lecturer_doc = BeautifulSoup(response.text, 'html.parser')
	return lecturer_doc

# 9th function
def encrypted_email_extraction(enc_email):

  # Given string
	input_string = str(enc_email)

	# Regular expression pattern to match data-cfemail value
	pattern = r'data-cfemail="([\w]+)"'

	# Extract data-cfemail value using regex
	matches = re.findall(pattern, input_string)

	# Print the extracted value
	if matches:
		cfemail_value = matches[0]
		print("Extracted data-cfemail value:", cfemail_value)
		return cfemail_value
	else:
		print("data-cfemail value not found in the input string.")

# 10th function
def cfDecodeEmail(encodedString):
	r = int(encodedString[:2], 16)
	email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
	return email

# 8th function
def get_lecturer_desc(lecturer_doc):

	name_selection_class = 'ExportFileName'
	name_tags = lecturer_doc.find_all('h2', {'class': name_selection_class})

	designation_selection_id = 'ctl00_cphContent_pDesignation'
	designation_tags = lecturer_doc.find_all('p', {'id': designation_selection_id})

	school_selection_id = 'ctl00_cphContent_pSchool'
	school_tags = lecturer_doc.find_all('p', {'id': school_selection_id})

	email_selection_id = 'ctl00_cphContent_aEmail'
	email_tags = lecturer_doc.find_all('a', {'id': email_selection_id})
	
	lecturer_dict = {'username': [], 'job_desc': [], 'department': [], 'email': []}
	for tags in name_tags:
		lecturer_dict['username'].append(tags.text.strip())
	for tags in designation_tags:
		lecturer_dict['job_desc'].append(tags.text.strip())
	for tags in school_tags:
		lecturer_dict['department'].append(tags.text.strip())
	for tags in email_tags:
		
		# email = tags['href'].split('#')[1]  # Extract the encoded email address
		lecturer_dict['email'].append(cfDecodeEmail(encrypted_email_extraction(tags)))
		# lecturer_dict['email'].append(tags.text.strip())
		

	return pandas.DataFrame(lecturer_dict)

# 3rd function
def get_faculty_name(doc):
	name_selection_class = 'person-name'
	name_tags = doc.find_all('td', {'class': name_selection_class})

	name_title = []
	for tags in name_tags:
		name_title.append(tags.text)
	
	return name_title

# 4th function
def get_faculty_jobdesc(doc):
	job_desc_selection_class = 'job-description'
	job_desc_tags = doc.find_all('td', {'class': job_desc_selection_class})
	job_desc = []
	for tags in job_desc_tags:
		job_desc.append(tags.text.strip())

	return job_desc

# 5th function
def get_faculty_url(doc):
	faculty_link_selection_class = 'person-name'
	faculty_link_tags = doc.find_all('td', {'class': faculty_link_selection_class})
	faculty_urls = []
	for tags in faculty_link_tags:
		a_tags = tags.find_all('a', href=True)
		for a_tag in a_tags:
			faculty_urls.append(a_tag['href'])
	return faculty_urls

# 2nd function
def scrape_names():
	# UMT faculty list URL
	faculty_url = 'https://www.umt.edu.pk/faculty.aspx'
	response = requests.get(faculty_url)
	page_content = response.text

	doc_parsing = BeautifulSoup(page_content, 'html.parser')

	# To check if UMT Faculty page is correctly loading or not
	if response.status_code != 200:
		raise Exception('Failed to load the page {}'.format(faculty_url))

  
	lecturer_dict = {
		'username': get_faculty_name(doc_parsing),
		'job_desc': get_faculty_jobdesc(doc_parsing),
		'url': get_faculty_url(doc_parsing)
	}

	return pandas.DataFrame(lecturer_dict)

# Scrape individual lecturer's information
def scrape_lecturer_info():
	print("Scraping list of Lecturer names")
	lecturer_dataframe = scrape_names()
	all_lecturers_data = []

	for index , row in lecturer_dataframe.iterrows():
		print('Scraping Lecturer {}'.format(row['username']))

		if '#' in row['url']:
			print('Skipping {} becuse the URL contains #'.format(row['username']))
			continue
		
		lecturer_doc = get_lecturer_page(row['url'])
		if lecturer_doc is None:
			print(f"Skipping {row['username']} because the page couldn't be fetched.")
			continue

		if not lecturer_doc.find_all('h2', {'class': 'ExportFileName'}):
			print('Skipping {} because username is missing'.format(row['username']))
			continue

		if not lecturer_doc.find_all('p', {'id': 'ctl00_cphContent_pDesignation'}):
			print('Skipping {} because designation is missing'.format(row['username']))
			continue

		if not lecturer_doc.find_all('p', {'id': 'ctl00_cphContent_pSchool'}):
			print('Skipping {} because school is missing'.format(row['username']))
			continue

		if not lecturer_doc.find_all('a', {'id': 'ctl00_cphContent_aEmail'}):
			print('Skipping {} because email is missing'.format(row['username']))
			continue
		
		lecturer_info = get_lecturer_desc(lecturer_doc)
		all_lecturers_data.append(lecturer_info)

		all_lecturers_df = pandas.concat(all_lecturers_data, ignore_index=True)
		all_lecturers_df.to_csv('all_lecturers.csv', index=False)


# start scraping UMT Faculty Directory
scrape_lecturer_info()
