from fastapi import FastAPI, HTTPException, Query  # type: ignore
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
import re

app = FastAPI()

@app.get("/v1/longSearch")
def scrape_wikipedia(query: str = Query(..., description="Wikipedia page title, e.g., Salman_Khan")):
    # Construct the external URL using the provided query as the title
    external_api_url = f"https://en.wikipedia.org/wiki/{query}"
    
    # Define headers to identify your bot/script
    headers = {
        'User-Agent': 'MyWikipediaBot/1.0 (https://example.com/mybot; myemail@example.com)'
    }
    
    # --- Fetch HTML Content ---
    try:
        response = requests.get(external_api_url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching URL: {e}")
    
    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # --- Extract Data ---
    
    # 1. Page Title
    page_title = soup.title.string.strip() if soup.title else "Title not found"
    
    # 2. Infobox Data (for biography pages, try multiple possible classes)
    infobox_data = {}
    # First try a common class; if not found, try a more generic one
    infobox = soup.find('table', class_='infobox biography vcard')
    if not infobox:
        infobox = soup.find('table', class_='infobox')
    
    if infobox:
        rows = infobox.find_all('tr')
        for row in rows:
            header_cell = row.find('th')
            data_cell = row.find('td')
            if header_cell and data_cell:
                label = header_cell.get_text(strip=True)
                value = None

                if label == 'Born':
                    birth_date_tag = data_cell.find('span', class_='bday')
                    birth_place_tag = data_cell.find('div', class_='birthplace')
                    birth_date = birth_date_tag.get_text(strip=True) if birth_date_tag else 'N/A'
                    # If birthplace element exists, use its text; otherwise, fallback to full cell text
                    birth_place_text = (birth_place_tag.get_text(strip=True, separator=', ')
                                        if birth_place_tag else data_cell.get_text(strip=True))
                    birth_place = re.sub(r'\s*,\s*', ', ', birth_place_text).strip()
                    value = f"{birth_date}, {birth_place}"
                    infobox_data['Birth Date'] = birth_date
                    infobox_data['Birth Place'] = birth_place

                elif label == 'Occupations':
                    occupations_list = data_cell.find_all('li')
                    if occupations_list:
                        value = [occ.get_text(strip=True) for occ in occupations_list]
                    else:
                        value = data_cell.get_text(strip=True)

                elif label == 'Years active':
                    value_text = data_cell.get_text(strip=True)
                    value = re.sub(r'\[.*?\]', '', value_text).strip().replace('\u2013', '-')

                elif label == 'Family':
                    family_link = data_cell.find('a')
                    value = family_link.get_text(strip=True) if family_link else data_cell.get_text(strip=True)

                else:
                    # For any other label, just extract the text
                    value = data_cell.get_text(" ", strip=True)

                if value:
                    infobox_data[label] = value
    else:
        infobox_data = "Infobox not found or data extraction failed"
    
    # 3. Introduction (First Non-Empty Paragraph)
    introduction = ""
    content_div = soup.find('div', id='mw-content-text')
    if content_div:
        potential_p = content_div.find('p')
        while potential_p and (not potential_p.get_text(strip=True) or potential_p.find(class_='hatnote')):
            potential_p = potential_p.find_next_sibling('p')
        if potential_p:
            introduction_text = potential_p.get_text()
            introduction = re.sub(r'\[\d+\]', '', introduction_text).strip()
            introduction = ' '.join(introduction.split())
        else:
            introduction = "First paragraph not reliably found."
    else:
        introduction = "Content section not found."
    
    # 4. Full Article Text (All paragraphs from main content)
    full_text = ""
    if content_div:
        paragraphs = content_div.find_all('p')
        full_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
    else:
        full_text = "Full text content not found."
    
    # Build and return the result
    result = {
        "requested_url": external_api_url,
        "page_title": page_title,
        "infobox_data": infobox_data,
        "introduction": introduction,
        "full_text": full_text,
        "html_length": len(html_content)
    }
    
    return result
