import requests
from bs4 import BeautifulSoup

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

    # Iterate over each <item> in the XML
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
