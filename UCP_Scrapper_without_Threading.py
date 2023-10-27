import requests
from bs4 import BeautifulSoup
import pandas
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


MAX_RETRIES = 5


def UCP_Faculty_Menu():
	# UCP Faculty Menu
	menu_items = {
		'1': 'faculty-of-pharmacy',
		'2': 'faculty-of-languages-literature',
		'3': 'faculty-of-information-technology-and-computer-science',
		'4': 'faculty-of-engineering',
		'5': 'faculty-of-media-and-mass-communication',
		'6': 'faculty-of-humanities-and-social-sciences',
		'7': 'faculty-of-science-technology',
		'8': 'faculty-of-management-sciences',
		'9': 'faculty-of-law',
		'0': 'Exit'
    }
	
	print("Faculty Menu:")
	for key, value in menu_items.items():
		print(f"{key}: {value}")
	while True:
		user_choice = input("Enter your choice: ")
		if user_choice in menu_items:
				return user_choice
		else:
				print("Invalid choice. Please try again.")


def UCP_Menu_Selection(choice):
	if choice == '1':
		print("You selected Faculty of Pharmacy.")
		faculty_url = 'https://ucp.edu.pk/faculty-of-pharmacy/faculty-members/'
		scrape_lecturer_info(faculty_url)
  
	elif choice == '2':
		print("You selected Faculty of Languages & Literature.")
		faculty_url = 'https://ucp.edu.pk/faculty-of-languages-literature/faculty-members/'
		scrape_lecturer_info(faculty_url)
	# Add code for Faculty of Languages & Literature here
	elif choice == '3':
		print("You selected Faculty of Information Technology and Computer Science.")
		faculty_url = 'https://ucp.edu.pk/faculty-of-information-technology-and-computer-science/faculty-members/'
		scrape_lecturer_info(faculty_url)
	# Add code for Faculty of Information Technology and Computer Science here
	elif choice == '4':
		print("You selected Faculty of Engineering.")
		faculty_url = 'https://ucp.edu.pk/faculty-of-engineering/faculty-members/'
		scrape_lecturer_info(faculty_url)
	# Add code for Faculty of Engineering here
	elif choice == '5':
		print("You selected Faculty of Media and Mass Communication.")
		faculty_url = 'https://ucp.edu.pk/faculty-of-media-and-mass-communication/faculty-members/'
		scrape_lecturer_info(faculty_url)
	# Add code for Faculty of Media and Mass Communication here
	elif choice == '6':
		print("You selected Faculty of Humanities and Social Sciences.")
		faculty_url = 'https://ucp.edu.pk/faculty-of-humanities-and-social-sciences/faculty-members/'
		scrape_lecturer_info(faculty_url)
	# Add code for Faculty of Humanities and Social Sciences here
	elif choice == '7':
		print("You selected Faculty of Science & Technology.")
		faculty_url = 'https://ucp.edu.pk/faculty-of-science-technology/faculty-members-2/'
		scrape_lecturer_info(faculty_url)
	# Add code for Faculty of Science & Technology here
	elif choice == '8':
		print("You selected Faculty of Management Sciences.")
		faculty_url = 'https://ucp.edu.pk/faculty-of-management-sciences/ucp-business-school/faculty-members/'
		scrape_lecturer_info(faculty_url)
	# Add code for Faculty of Management Sciences here
	elif choice == '9':
		print("You selected Faculty of Law.")
		faculty_url = 'https://ucp.edu.pk/faculty-of-law/faculty-members/'
		scrape_lecturer_info(faculty_url)
	# Add code for Faculty of Law here
	elif choice == '0':
		print("Exiting the program.")
	else:
		print("Invalid choice.")

# 7th function
def get_lecturer_page(lecturer_url):
	session = requests.Session()
	retries = Retry(total=MAX_RETRIES, backoff_factor=0.1, status_forcelist=[ 500, 502, 503, 504 ])
	session.mount('http://', HTTPAdapter(max_retries=retries))
	session.mount('https://', HTTPAdapter(max_retries=retries))

	try:
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

		response = session.get(lecturer_url , headers=headers)
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


# 8th function
def get_lecturer_desc(lecturer_doc):

	name_selection_class = 'item-title'
	name_tags = lecturer_doc.find_all('h3', {'class': name_selection_class})

	designation_selection_id = 'small-text'
	designation_tags = lecturer_doc.find_all('h4', {'class': designation_selection_id})



	email_selection_id = 'extra-info'
	email_tags = lecturer_doc.find_all('div', {'class': email_selection_id})
	
	lecturer_dict = {'username': [], 'job_desc': [],'email': []}

	for tags in name_tags:
		lecturer_dict['username'].append(tags.text.strip())
	
	for tags in designation_tags:
		lecturer_dict['job_desc'].append(tags.text.strip())

	for tags in email_tags:
		lecturer_dict['email'].append(tags.text.strip())
	
		

	return pandas.DataFrame(lecturer_dict)

# 3rd function
def get_faculty_name(doc):

	name_selection_class = 'main-color-1-hover'
	name_tags = doc.find_all('a', {'class': name_selection_class})
	
	name_title = []

	for tags in name_tags:
		
		name_title.append(tags.text.strip())
		

	job_desc_selection_class = 'small-text'
	job_desc_tags = doc.find_all('h4', {'class': job_desc_selection_class})
	
	job_desc = []
	for tags in job_desc_tags:
		job_desc.append(tags.text.strip())
	
	print(len(name_title))
	print(str(name_title) + " " + str(job_desc))
	return name_title

# 4th function
def get_faculty_jobdesc(doc):

	job_desc_selection_class = 'small-text'
	job_desc_tags = doc.find_all('h4', {'class': job_desc_selection_class})
	
	job_desc = []
	for tags in job_desc_tags:
		job_desc.append(tags.text.strip())

	print(len(job_desc))
	return job_desc

# 5th function
def get_faculty_url(doc):
	faculty_link_selection_class = 'item-thumbnail'
	faculty_link_tags = doc.find_all('div', {'class': faculty_link_selection_class})
	faculty_urls = []
	for tags in faculty_link_tags:
		a_tags = tags.find_all('a', href=True)
		for a_tag in a_tags:
			faculty_urls.append(a_tag['href'])
		
	
	print(len(faculty_urls))
	return faculty_urls

# 2nd function
def scrape_names(faculty_url):

	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
	response = requests.get(faculty_url, headers=headers)
	page_content = response.text

	doc_parsing = BeautifulSoup(page_content, 'html.parser')

	# To check if UMT Faculty page is correctly loading or not
	if response.status_code != 200:
		raise Exception('Failed to load the page {}'.format(faculty_url))

	faculty_link_selection_class = 'item-title'
	faculty_link_tags = doc_parsing.find_all('h3', {'class': faculty_link_selection_class})
	faculty_urls = []
	name = []

	for tags in faculty_link_tags:
		a_tags = tags.find_all('a', href=True)
		for a_tag in a_tags:
			name.append(a_tag.text.strip())
			faculty_urls.append(a_tag['href'])

	lecturer_dict = {
		'username': name,
		'url' : faculty_urls
	}		
		

    # min_length = min(len(lecturer_dict['username']), len(lecturer_dict['job_desc']), len(lecturer_dict['email']))
		# lecturer_dict['username'] = lecturer_dict['username'][:min_length]
    # lecturer_dict['job_desc'] = lecturer_dict['job_desc'][:min_length]
    # lecturer_dict['email'] = lecturer_dict['email'][:min_length]

			
	return pandas.DataFrame(lecturer_dict)

# Scrape individual lecturer's information
def scrape_lecturer_info(faculty_url):
	url_parts = faculty_url.split('/')
	# Extract the desired part
	faculty_name = url_parts[3]
	# print(faculty_name)
	print("Scraping list of Lecturer names")
	lecturer_dataframe = scrape_names(faculty_url)
	all_lecturers_data = []
	print("Loading...")
	for index , row in lecturer_dataframe.iterrows():
		#print('Scraping Lecturer {}'.format(row['username']))
		

		if '#' in row['url']:
			print('Skipping {} becuse the URL contains #'.format(row['username']))
			continue
		
		lecturer_doc = get_lecturer_page(row['url'])
		if lecturer_doc is None:
			print(f"Skipping {row['username']} because the page couldn't be fetched.")
			continue

		if not lecturer_doc.find_all('h3', {'class': 'item-title'}):
			print('Skipping {} because username is missing'.format(row['username']))
			continue

		if not lecturer_doc.find_all('h4', {'class': 'small-text'}):
			print('Skipping {} because designation is missing'.format(row['username']))
			continue

		if not lecturer_doc.find_all('div', {'class': 'extra-info'}):
			print('Skipping {} because school is missing'.format(row['username']))
			continue

		

		lecturer_info = get_lecturer_desc(lecturer_doc)
		all_lecturers_data.append(lecturer_info)

		all_lecturers_df = pandas.concat(all_lecturers_data, ignore_index=True)
		all_lecturers_df.to_csv(str(faculty_name)+'_lecturers.csv', index=False)


# start scraping UCP Faculty Directory
# scrape_lecturer_info()
UCP_Menu_Selection(UCP_Faculty_Menu())