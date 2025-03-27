import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib.parse

def biorxiv_most_recent_30__posts():
    url = "https://connect.biorxiv.org/biorxiv_xml.php?subject=all"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to retrieve data: {response.status_code}")

# Function to search for keywords in text
def _contains_keywords(text, keywords):
    return any(keyword.lower() in text.lower() for keyword in keywords)


def biorxiv_recent_posts_filtered(keywords = ["caenorhabditis", "elegans"]):
    xml_data = biorxiv_most_recent_30__posts()
    soup = BeautifulSoup(xml_data, "xml")
    articles = []

    for item in soup.find_all('item'):
        title = item.find('title').get_text(strip=True)
        description = item.find('description').get_text(strip=True)
        dc_date = item.find('dc:date').get_text(strip=True)
        dc_identifier = item.find('dc:identifier').get_text(strip=True)
        
        # Check if either the title or description contains any of the keywords
        if _contains_keywords(title, keywords) or _contains_keywords(description, keywords):
            # Append the article details as a dictionary
            articles.append({
                'title': title,
                'date': dc_date,
                'doi': f"https://doi.org/{dc_identifier}"
            })

    return articles


def biorxiv_search(search_criteria="caenorhabditis elegans", days=1):
    result_dict = []  # Initialize an empty list to return

    try:
        url = encode_biorxiv_search(search_criteria, days)
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            search_results_div = soup.find('div', class_='panel-pane pane-highwire-search-results active', id='hw-advance-search-result')

            if search_results_div:
                for li in search_results_div.find_all('li'):
                    a_tag = li.find('a', class_='highwire-cite-linked-title')
                    if a_tag:
                        # Extract the href and title
                        url = a_tag['href']
                        title = a_tag.find('span', class_='highwire-cite-title').text

                        # Create a dictionary for each entry
                        result_dict.append({'url': f"https://www.biorxiv.org{url}", 'title': title})
            else:
                print("Specified div not found.")
        else:
            print(f"Request failed with status code {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

    return result_dict  # Return the result (could be empty if there was an error)

def encode_biorxiv_search(search_criteria, days=1):
    base_url = "https://www.biorxiv.org/search/"
    today = datetime.today()
    start_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    # Construct the query string with placeholders
    query_string = f"abstract_title:{search_criteria} abstract_title_flags:match-any jcode:biorxiv limit_from:{start_date} limit_to:{end_date} numresults:75 sort:publication-date direction:ascending format_result:condensed"
    
    # Encode the query string
    encoded_query = urllib.parse.quote(query_string)
    
    # Combine the base URL with the encoded query string
    full_url = base_url + encoded_query
    return full_url

