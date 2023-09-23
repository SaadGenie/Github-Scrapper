import requests
import os
from bs4 import BeautifulSoup
import pandas

url = "https://github.com/topics"
response = requests.get(url)
page_content = response.text


doc = BeautifulSoup(page_content , 'html.parser')

def get_topic_page(topic_url):
	response = requests.get(topic_url)
	
	if response.status_code != 200:
		raise Exception('Failed to load the page {}'.format(topic_url))
	
	topic_doc = BeautifulSoup(response.text , 'html.parser')

	return topic_doc


def get_repo_info(h3_tag , star_tags):
	# returns all the required info about a repository 
	a_tags = h3_tag.find_all('a')
	username = a_tags[0].text.strip()
	repo_name = a_tags[1].text.strip()
	base_url = "https://github.com"
	repo_url = base_url + a_tags[1]['href']
	stars = parse_star_count(star_tags.text.strip())
	return username , repo_name , stars , repo_url


def get_topic_repo(topic_doc):
	
	div_selection_class = 'f3 color-fg-muted text-normal lh-condensed'
	repo_tags = topic_doc.find_all('h3' , {'class': div_selection_class})
	star_selection_class = 'Counter js-social-count'
	star_tags = topic_doc.find_all('span' , {'class': star_selection_class})
	
	topic_repo_dict = { 'username': [], 'repo_name': [], 'stars' : [], 'repo_url': [] }
	for i in range(len(repo_tags)):
		repo_info = get_repo_info(repo_tags[i] , star_tags[i])
		topic_repo_dict['username'].append(repo_info[0])
		topic_repo_dict['repo_name'].append(repo_info[1])
		topic_repo_dict['stars'].append(repo_info[2])
		topic_repo_dict['repo_url'].append(repo_info[3])
		
	return pandas.DataFrame(topic_repo_dict)

def parse_star_count(stars_str):
	stars_str = stars_str.strip()

	if stars_str[-1] == 'k':
		return int(float(stars_str[:-1])*1000)
	
	return int(stars_str)

def get_topic_titles(doc):
	title_selection_class = 'f3 lh-condensed mb-0 mt-1 Link--primary'
	topic_title_tags = doc.find_all('p' , {'class': title_selection_class})

	topic_title = []
	for tags in topic_title_tags:
		topic_title.append(tags.text)
	
	return topic_title


def get_topic_desc(doc):
	desc_selection_class = 'f5 color-fg-muted mb-0 mt-1'
	topic_desc_tags = doc.find_all('p', {'class': desc_selection_class})
	topic_desc = []
	for tags in topic_desc_tags:
		topic_desc.append(tags.text.strip())

	return topic_desc

def get_topic_url(doc):

	link_selection_class = 'no-underline flex-grow-0'
	topic_link_tags = doc.find_all('a' , {'class': link_selection_class})

	topic_url = []
	base_url = "https://github.com"

	for tags in topic_link_tags:
		topic_url.append(base_url + tags['href'])

	return topic_url


def scrape_topics():
	topics_url = 'https://github.com/topics'
	response = requests.get(topics_url)
	if response.status_code != 200:
		raise Exception('Failed to load the page {}'.format(topics_url))

	topics_dict = {
		'title': get_topic_titles(doc),
		'description': get_topic_desc(doc),
		'url': get_topic_url(doc)
	}

	return pandas.DataFrame(topics_dict)

def scrape_topic(topic_url, topic_name):
    # Create a folder named 'data' if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

    file_path = os.path.join('data', topic_name + '.csv')

    if os.path.exists(file_path):
        print(f"{topic_name}.csv already exists. Skipping...")
        return

    topic_dataframe = get_topic_repo(get_topic_page(topic_url))
    topic_dataframe.to_csv(file_path, index=None)

def scrape_topics_repos():
	print("Scrapping list of topic")
	topics_dataframe = scrape_topics()
	for index , row in  topics_dataframe.iterrows():
		print('Scraping top repositories for {}'.format(row['title']))
		scrape_topic(row['url'], row['title'])



scrape_topics_repos()
