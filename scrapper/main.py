from fastapi import FastAPI, HTTPException, Query # type: ignore
import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
import re
from typing import Dict, List, Any, Optional
import json
from urllib.parse import urljoin, unquote

app = FastAPI()

@app.get("/v1/longSearch")
def scrape_wikipedia(query: str = Query(..., description="Wikipedia page title, e.g., 'Albert_Einstein', 'New_York_City', 'World_War_II'")):
    # Clean up the query to handle URL-encoded characters
    query = unquote(query)
    
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
    
    # Check if the page is a disambiguation page
    if is_disambiguation_page(soup):
        return extract_disambiguation_page(soup, external_api_url)
    
    # --- Extract Data ---
    
    # 1. Page Title and basic metadata
    page_metadata = extract_page_metadata(soup, external_api_url)
    
    # 2. Determine page type and extract appropriate infobox data
    page_type, infobox_data = extract_infobox_and_determine_type(soup)
    
    # 3. Introduction (First Non-Empty Paragraph)
    introduction = extract_introduction(soup)
    
    # 4. Table of Contents
    toc = extract_table_of_contents(soup)
    
    # 5. Extract all sections with their content
    sections = extract_sections(soup)
    
    # 6. Extract all images with their captions
    images = extract_images(soup)
    
    # 7. Extract all tables
    tables = extract_tables(soup)
    
    # 8. Extract references/citations
    references = extract_references(soup)
    
    # 9. Extract categories
    categories = extract_categories(soup)
    
    # 10. Extract external links
    external_links = extract_external_links(soup)
    
    # 11. Related Wikipedia pages (internal links)
    related_pages = extract_related_pages(soup)
    
    # 12. Extract coordinates (for geographical articles)
    coordinates = extract_coordinates(soup)
    
    # 13. Extract language links
    language_links = extract_language_links(soup)
    
    # 14. Extract special data based on page type
    special_data = extract_special_data(soup, page_type, infobox_data, sections)
    
    # 15. Generate summary
    summary = generate_summary(introduction, sections, page_type)
    
    # 16. Extract lists (if available)
    lists = extract_lists(soup)
    
    # 17. Extract hatnotes and disambiguation info
    disambiguation_info = extract_disambiguation(soup)
    
    # 18. Extract taxonomic classification (for species pages)
    taxonomic_data = extract_taxonomic_data(soup) if page_type == "species" else {}
    
    # 19. Extract associated media (audio, video)
    media = extract_media(soup)
    
    # 20. Extract page statistics
    page_stats = extract_page_stats(soup)
    
    # Build and return the result
    result = {
        "page_metadata": page_metadata,
        "page_type": page_type,
        "summary": summary,
        "infobox_data": infobox_data,
        "introduction": introduction,
        "table_of_contents": toc,
        "sections": sections,
        "images": images,
        "tables": tables,
        "lists": lists,
        "coordinates": coordinates,
        "references": references,
        "external_links": external_links,
        "related_pages": related_pages,
        "language_links": language_links,
        "categories": categories,
        "special_data": special_data,
        "disambiguation_info": disambiguation_info,
        "taxonomic_data": taxonomic_data,
        "media": media,
        "page_stats": page_stats,
        "html_length": len(html_content)
    }
    
    # Remove empty fields for cleaner output
    result = {k: v for k, v in result.items() if v}
    
    return result

def is_disambiguation_page(soup: BeautifulSoup) -> bool:
    """Check if the current page is a disambiguation page."""
    # Check for disambiguation notice
    disambig_div = soup.find('div', {'class': 'disambiguation'})
    if disambig_div:
        return True
    
    # Check for category links
    category_links = soup.find_all('a', href=lambda href: href and 'Category:Disambiguation_pages' in href)
    if category_links:
        return True
    
    # Check title for disambiguation indication
    title = soup.title.string if soup.title else ""
    if " (disambiguation)" in title:
        return True
    
    return False

def extract_disambiguation_page(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """Extract data from a disambiguation page."""
    # Basic page metadata
    page_metadata = extract_page_metadata(soup, url)
    
    # Extract introduction
    introduction = extract_introduction(soup)
    
    # Extract disambiguation options
    options = []
    content_div = soup.find('div', {'id': 'mw-content-text'})
    if content_div:
        # Find all lists
        lists = content_div.find_all('ul')
        for ul in lists:
            list_items = ul.find_all('li')
            for item in list_items:
                option = {}
                
                # Extract main link
                main_link = item.find('a')
                if main_link and not main_link.get('class'):  # Skip hatnote links
                    option['title'] = main_link.get_text(strip=True)
                    option['url'] = urljoin(url, main_link.get('href', ''))
                    
                    # Extract description
                    # Remove the link text from the item text to get the description
                    full_text = item.get_text(strip=True)
                    if main_link.get_text(strip=True) in full_text:
                        description = full_text.replace(main_link.get_text(strip=True), '', 1).strip()
                        # Remove leading punctuation
                        description = re.sub(r'^[,\s:–\-]+', '', description).strip()
                        if description:
                            option['description'] = description
                    
                    options.append(option)
    
    return {
        "page_metadata": page_metadata,
        "page_type": "disambiguation",
        "introduction": introduction,
        "disambiguation_options": options
    }

def extract_page_metadata(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """Extract basic page metadata."""
    metadata = {
        "title": soup.title.string.strip() if soup.title else "Title not found",
        "url": url,
        "canonical_url": "",
        "description": "",
        "last_modified": "",
        "protection_status": {},
        "talk_page": "",
        "view_history": ""
    }
    
    # Extract page title without " - Wikipedia" suffix
    if " - Wikipedia" in metadata["title"]:
        metadata["title"] = metadata["title"].split(" - Wikipedia")[0].strip()
    
    # Extract canonical URL
    canonical_link = soup.find('link', rel='canonical')
    if canonical_link and canonical_link.get('href'):
        metadata["canonical_url"] = canonical_link['href']
    
    # Extract meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        metadata["description"] = meta_desc['content']
    
    # Extract last modified date
    footer_info = soup.find('li', id='footer-info-lastmod')
    if footer_info:
        metadata["last_modified"] = footer_info.get_text(strip=True)
    
    # Extract protection status
    protection_banner = soup.find('div', {'id': 'mw-indicator-protection-status'})
    if protection_banner:
        protection_links = protection_banner.find_all('a')
        for link in protection_links:
            protection_type = link.get('title', '')
            if protection_type:
                metadata["protection_status"][protection_type] = True
    
    # Extract talk page link
    talk_tab = soup.find('li', id='ca-talk')
    if talk_tab and talk_tab.find('a'):
        talk_link = talk_tab.find('a').get('href', '')
        if talk_link:
            metadata["talk_page"] = urljoin(url, talk_link)
    
    # Extract view history link
    history_tab = soup.find('li', id='ca-history')
    if history_tab and history_tab.find('a'):
        history_link = history_tab.find('a').get('href', '')
        if history_link:
            metadata["view_history"] = urljoin(url, history_link)
    
    return metadata

def extract_infobox_and_determine_type(soup: BeautifulSoup) -> tuple:
    """Extract infobox data and determine the page type based on infobox class and content."""
    page_type = "unknown"
    infobox_data = {}
    
    # Try to find any infobox
    infobox = soup.find('table', class_=lambda c: c and 'infobox' in c)
    
    if infobox:
        # Store infobox class as it helps determine content type
        infobox_classes = infobox.get('class', [])
        infobox_data["_infobox_class"] = ' '.join(infobox_classes)
        
        # Determine page type based on infobox class
        if any(cls in ' '.join(infobox_classes) for cls in ['biography', 'vcard']):
            page_type = "person"
        elif any(cls in ' '.join(infobox_classes) for cls in ['geography', 'settlement', 'country', 'SettlementBox']):
            page_type = "place"
        elif any(cls in ' '.join(infobox_classes) for cls in ['species', 'taxobox']):
            page_type = "species"
        elif any(cls in ' '.join(infobox_classes) for cls in ['organization', 'company']):
            page_type = "organization"
        elif any(cls in ' '.join(infobox_classes) for cls in ['event', 'conflict']):
            page_type = "event"
        elif any(cls in ' '.join(infobox_classes) for cls in ['book', 'album', 'film', 'television', 'game']):
            page_type = "media"
        elif any(cls in ' '.join(infobox_classes) for cls in ['building', 'structure']):
            page_type = "structure"
        
        # Extract caption if available
        caption = infobox.find('caption')
        if caption:
            infobox_data["_title"] = caption.get_text(strip=True)
        
        # Extract all rows from the infobox
        rows = infobox.find_all('tr')
        
        # Process each row in the infobox
        for row in rows:
            header_cell = row.find('th')
            data_cell = row.find('td')
            
            # Row with header and data
            if header_cell and data_cell:
                label = header_cell.get_text(strip=True)
                
                # Process common infobox fields based on the label
                process_infobox_field(label, data_cell, infobox_data, page_type)
            
            # Row with just an image (common in many infoboxes)
            elif not header_cell and data_cell:
                extract_infobox_image(data_cell, infobox_data)
    
    # Additional page type detection based on categories
    if page_type == "unknown":
        categories = soup.find('div', id='mw-normal-catlinks')
        if categories:
            cat_text = categories.get_text().lower()
            
            if any(term in cat_text for term in ['person', 'people', 'births', 'deaths']):
                page_type = "person"
            elif any(term in cat_text for term in ['city', 'town', 'country', 'place', 'geography']):
                page_type = "place"
            elif any(term in cat_text for term in ['species', 'animal', 'plant', 'fungus']):
                page_type = "species"
            elif any(term in cat_text for term in ['organization', 'company', 'corporation']):
                page_type = "organization"
            elif any(term in cat_text for term in ['event', 'conflict', 'war', 'battle']):
                page_type = "event"
            elif any(term in cat_text for term in ['book', 'film', 'movie', 'album', 'television']):
                page_type = "media"
            elif any(term in cat_text for term in ['concept', 'theory', 'philosophy']):
                page_type = "concept"
    
    # If still unknown, try to determine from content
    if page_type == "unknown":
        intro = extract_introduction(soup)
        intro_lower = intro.lower()
        
        if any(term in intro_lower for term in [' born ', ' died ', 'is an american', 'is a british']):
            page_type = "person"
        elif any(term in intro_lower for term in ['city', 'town', 'capital', 'country', 'region']):
            page_type = "place"
        elif any(term in intro_lower for term in ['species', 'genus', 'family', 'phylum']):
            page_type = "species"
        elif any(term in intro_lower for term in ['company', 'corporation', 'organization', 'founded']):
            page_type = "organization"
        elif any(term in intro_lower for term in ['event', 'conflict', 'war', 'battle', 'took place']):
            page_type = "event"
        elif any(term in intro_lower for term in ['book', 'novel', 'film', 'movie', 'album', 'tv series']):
            page_type = "media"
        elif any(term in intro_lower for term in ['concept', 'theory', 'philosophy', 'refers to']):
            page_type = "concept"
    
    return page_type, infobox_data

def process_infobox_field(label: str, data_cell: BeautifulSoup, infobox_data: Dict[str, Any], page_type: str):
    """Process an infobox field based on its label and page type."""
    label_lower = label.lower()
    clean_label = re.sub(r'\[\d+\]', '', label).strip()
    
    # Person-specific fields
    if page_type == "person" and label_lower in ['born', 'birth date', 'date of birth']:
        extract_birth_info(data_cell, infobox_data)
    
    elif page_type == "person" and label_lower in ['died', 'death date', 'date of death']:
        extract_death_info(data_cell, infobox_data)
    
    elif page_type == "person" and label_lower in ['spouse', 'spouses', 'partner', 'partners']:
        extract_relationship_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "person" and label_lower in ['occupations', 'occupation', 'profession', 'professions']:
        extract_list_or_text(data_cell, infobox_data, clean_label)
    
    elif page_type == "person" and label_lower in ['known for', 'notable works', 'works']:
        extract_list_or_text(data_cell, infobox_data, clean_label)
    
    elif page_type == "person" and label_lower in ['education', 'alma mater', 'school']:
        extract_list_or_text(data_cell, infobox_data, clean_label)
    
    # Place-specific fields
    elif page_type == "place" and label_lower in ['population', 'population total']:
        extract_population_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "place" and label_lower in ['area', 'area total']:
        extract_area_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "place" and label_lower in ['coordinates', 'location', 'position']:
        extract_location_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "place" and label_lower in ['country', 'state', 'province', 'region']:
        extract_administrative_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "place" and label_lower in ['time zone', 'climate', 'elevation']:
        extract_generic_field(data_cell, infobox_data, clean_label)
    
    # Organization-specific fields
    elif page_type == "organization" and label_lower in ['founded', 'formation', 'established']:
        extract_date_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "organization" and label_lower in ['headquarters', 'location']:
        extract_location_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "organization" and label_lower in ['key people', 'leaders', 'ceo', 'chairman']:
        extract_people_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "organization" and label_lower in ['industry', 'sector', 'revenue', 'employees']:
        extract_generic_field(data_cell, infobox_data, clean_label)
    
    # Event-specific fields
    elif page_type == "event" and label_lower in ['date', 'period', 'duration']:
        extract_date_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "event" and label_lower in ['location', 'place', 'venue']:
        extract_location_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "event" and label_lower in ['participants', 'combatants']:
        extract_participants_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "event" and label_lower in ['casualties', 'result', 'outcome']:
        extract_generic_field(data_cell, infobox_data, clean_label)
    
    # Media-specific fields
    elif page_type == "media" and label_lower in ['author', 'director', 'producer', 'creator']:
        extract_people_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "media" and label_lower in ['release date', 'published', 'publication date']:
        extract_date_info(data_cell, infobox_data, clean_label)
    
    elif page_type == "media" and label_lower in ['genre', 'language', 'budget', 'box office']:
        extract_generic_field(data_cell, infobox_data, clean_label)
    
    # Species-specific fields
    elif page_type == "species" and label_lower in ['kingdom', 'phylum', 'class', 'order', 'family', 'genus']:
        extract_taxonomic_field(data_cell, infobox_data, clean_label)
    
    elif page_type == "species" and label_lower in ['binomial', 'conservation status', 'range']:
        extract_generic_field(data_cell, infobox_data, clean_label)
    
    # Structure-specific fields
    elif page_type == "structure" and label_lower in ['architect', 'architecture', 'built', 'height']:
        extract_generic_field(data_cell, infobox_data, clean_label)
    
    # Concept-specific fields
    elif page_type == "concept" and label_lower in ['field', 'sub-fields', 'main proponents']:
        extract_list_or_text(data_cell, infobox_data, clean_label)
    
    # Common fields for all page types
    elif label_lower in ['website', 'url', 'homepage']:
        extract_website_info(data_cell, infobox_data, clean_label)
    
    elif label_lower in ['image', 'map', 'photo', 'flag', 'logo']:
        extract_infobox_image(data_cell, infobox_data, clean_label)
    
    # Default extraction for any other field
    else:
        extract_generic_field(data_cell, infobox_data, clean_label)

def extract_generic_field(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    """Extract data from a generic infobox field."""
    # First try to find any links
    links = data_cell.find_all('a')
    if links:
        # If there are multiple links, store as a list
        if len(links) > 1:
            link_data = []
            for link in links:
                link_text = link.get_text(strip=True)
                if link_text:  # Only add non-empty links
                    link_data.append(link_text)
            if link_data:  # Only store if we found valid links
                infobox_data[label] = link_data
        else:
            # Single link - store as string
            link_text = links[0].get_text(strip=True)
            if link_text:
                infobox_data[label] = link_text
    else:
        # No links found, try to get plain text
        text = data_cell.get_text(strip=True)
        if text:
            # Try to convert to number if it looks like one
            if text.replace(',', '').replace('.', '').replace('-', '').isdigit():
                # Handle comma-separated numbers and convert to float if decimal
                clean_num = text.replace(',', '')
                if '.' in clean_num:
                    try:
                        infobox_data[label] = float(clean_num)
                    except ValueError:
                        infobox_data[label] = text
                else:
                    try:
                        infobox_data[label] = int(clean_num)
                    except ValueError:
                        infobox_data[label] = text
            else:
                infobox_data[label] = text

def extract_infobox_image(data_cell: BeautifulSoup, infobox_data: Dict[str, Any]):
    """Extract image information from an infobox cell."""
    # Look for image elements
    img = data_cell.find('img')
    if img:
        image_data = {
            "src": img.get('src', ''),
            "alt": img.get('alt', ''),
            "width": img.get('width', ''),
            "height": img.get('height', '')
        }
        
        # Clean up src URL to get full resolution if it's a thumbnail
        if image_data["src"].startswith('//'):
            image_data["src"] = 'https:' + image_data["src"]
        
        # Look for caption
        caption_div = data_cell.find('div', class_='infobox-caption')
        if caption_div:
            image_data["caption"] = caption_div.get_text(strip=True)
        
        # Store in infobox data
        if "images" not in infobox_data:
            infobox_data["images"] = []
        infobox_data["images"].append(image_data)

def extract_birth_info(data_cell: BeautifulSoup, infobox_data: Dict[str, Any]):
    """Extract detailed birth information for person pages."""
    birth_info = {}
    
    # Extract birth date
    birth_date_tag = data_cell.find('span', class_='bday')
    if birth_date_tag:
        birth_info['date'] = birth_date_tag.get_text(strip=True)
    
    # Extract age if available
    age_tag = data_cell.find('span', class_='noprint ForceAgeToShow')
    if age_tag:
        age_text = age_tag.get_text(strip=True)
        age_match = re.search(r'age\s+(\d+)', age_text, re.IGNORECASE)
        if age_match:
            birth_info['age'] = age_match.group(1)
    
    # Extract birth place
    birth_place_tag = data_cell.find('div', class_='birthplace')
    if birth_place_tag:
        birth_info['place'] = birth_place_tag.get_text(strip=True, separator=', ')
    else:
        # Try to extract birth place from text
        cell_text = data_cell.get_text(strip=True)
        if 'date' in birth_info:
            # Remove the birth date and clean up
            place_text = re.sub(birth_info['date'], '', cell_text).strip()
            # Remove age information if present
            if 'age' in birth_info:
                place_text = re.sub(r'\(\s*age\s+\d+\s*\)', '', place_text).strip()
            # Clean up remaining text
            place_text = re.sub(r'^\s*\(\s*', '', place_text)
            place_text = re.sub(r'\s*\)\s*$', '', place_text)
            if place_text:
                birth_info['place'] = place_text
    
    # Look for links to extract more structured information about the birthplace
    place_links = data_cell.find_all('a')
    if place_links:
        birthplace_parts = []
        for link in place_links:
            link_text = link.get_text(strip=True)
            # Skip reference numbers and date parts
            if (link_text and not link_text.isdigit() and 
                not re.match(r'^(January|February|March|April|May|June|July|August|September|October|November|December|\d+)$', link_text)):
                birthplace_parts.append({
                    "name": link_text,
                    "url": urljoin('https://en.wikipedia.org', link.get('href', ''))
                })
        if birthplace_parts:
            birth_info['place_parts'] = birthplace_parts
    
    if birth_info:
        infobox_data['Birth'] = birth_info

def extract_death_info(data_cell: BeautifulSoup, infobox_data: Dict[str, Any]):
    """Extract detailed death information for person pages."""
    death_info = {}
    
    # Extract death date
    death_date_tag = data_cell.find('span', class_='dday')
    if death_date_tag:
        death_info['date'] = death_date_tag.get_text(strip=True)
    
    # If no specific class, try to extract from raw text
    if 'date' not in death_info:
        date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', data_cell.get_text(strip=True))
        if date_match:
            death_info['date'] = date_match.group(1)
    
    # Extract death place
    death_place_tag = data_cell.find('div', class_='deathplace')
    if death_place_tag:
        death_info['place'] = death_place_tag.get_text(strip=True, separator=', ')
    else:
        # Try to extract death place from text
        cell_text = data_cell.get_text(strip=True)
        if 'date' in death_info:
            # Remove the death date and clean up
            place_text = re.sub(death_info['date'], '', cell_text).strip()
            place_text = re.sub(r'^\s*\(\s*', '', place_text)
            place_text = re.sub(r'\s*\)\s*$', '', place_text)
            
            # Remove age at death if present
            place_text = re.sub(r'\(aged\s+\d+\)', '', place_text).strip()
            
            if place_text:
                death_info['place'] = place_text
    
    # Extract cause of death if mentioned
    cell_text = data_cell.get_text(strip=True)
    cause_match = re.search(r'(?:cause of death|died from|died of)[:\s]+([^)]+)', cell_text, re.IGNORECASE)
    if cause_match:
        death_info['cause'] = cause_match.group(1).strip()
    
    # Extract age at death
    age_match = re.search(r'\(aged\s+(\d+)\)', cell_text, re.IGNORECASE)
    if age_match:
        death_info['age_at_death'] = age_match.group(1)
    
    if death_info:
        infobox_data['Death'] = death_info

def extract_relationship_info(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    """Extract detailed relationship information for person pages."""
    relationships = []
    
    # Look for list items first (multiple spouses/partners)
    spouse_items = data_cell.find_all('li')
    
    if spouse_items:
        for item in spouse_items:
            relationship = {}
            
            # Extract name
            name_link = item.find('a')
            if name_link:
                relationship['name'] = name_link.get_text(strip=True)
                relationship['url'] = urljoin('https://en.wikipedia.org', name_link.get('href', ''))
            else:
                text = item.get_text(strip=True)
                # Clean citation references
                text = re.sub(r'\[\d+\]', '', text)
                relationship['text'] = text
            
            # Extract marriage date/period if available
            text = item.get_text(strip=True)
            
            # Look for marriage dates
            marriage_dates = re.search(r'\(\s*(?:m\.|married)\s*([\d\w\s\-–]+)(?:(?:;|,|\s+to\s+)?\s*(?:div\.|divorced)\s*([\d\w\s\-–]+))?\s*\)', text, re.IGNORECASE)
            if marriage_dates:
                if marriage_dates.group(1):
                    relationship['marriage_date'] = marriage_dates.group(1).strip()
                if marriage_dates.group(2):
                    relationship['divorce_date'] = marriage_dates.group(2).strip()
            
            # If no specific marriage marker, look for date ranges in parentheses
            if 'marriage_date' not in relationship and 'text' in relationship:
                date_range = re.search(r'\(\s*([\d\w\s\-–]+)\s*(?:to|–|-)\s*([\d\w\s\-–]+|\bpresent\b)\s*\)', text, re.IGNORECASE)
                if date_range:
                    relationship['start_date'] = date_range.group(1).strip()
                    relationship['end_date'] = date_range.group(2).strip()
            
            if relationship:
                relationships.append(relationship)
    else:
        # If no list items, extract from the entire cell
        relationship = {}
        
        # Extract name
        name_link = data_cell.find('a')
        if name_link:
            relationship['name'] = name_link.get_text(strip=True)
            relationship['url'] = urljoin('https://en.wikipedia.org', name_link.get('href', ''))
        else:
            text = data_cell.get_text(strip=True)
            # Clean citation references
            text = re.sub(r'\[\d+\]', '', text)
            relationship['text'] = text
        
        # Extract marriage date/period if available
        text = data_cell.get_text(strip=True)
        
        # Look for date patterns
        date_patterns = [
            r'\(\s*(?:m\.|married)\s*([\d\w\s\-–]+)\s*\)',  # married date
            r'\(\s*([\d\w\s\-–]+)\s*(?:to|–|-)\s*([\d\w\s\-–]+|\bpresent\b)\s*\)'  # date range
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                if len(date_match.groups()) == 1:
                    relationship['date'] = date_match.group(1).strip()
                elif len(date_match.groups()) == 2:
                    relationship['start_date'] = date_match.group(1).strip()
                    relationship['end_date'] = date_match.group(2).strip()
                break
        
        if relationship:
            relationships.append(relationship)
    
    if relationships:
        infobox_data[label] = relationships

def extract_list_or_text(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    list_items = data_cell.find_all('li')
    if list_items:
        items = []
        for item in list_items:
            item_data = {
                "text": item.get_text(strip=True)
            }
            link = item.find('a')
            if link:
                item_data["url"] = urljoin('https://en.wikipedia.org', link.get('href', ''))
            items.append(item_data)
        infobox_data[label] = items
    else:
        text = data_cell.get_text(strip=True)
        if text:
            infobox_data[label] = text

def extract_introduction(soup: BeautifulSoup) -> str:
    paragraphs = soup.select("#mw-content-text .mw-parser-output > p")
    for para in paragraphs:
        text = para.get_text(strip=True)
        if text:
            return text
    return ""

def extract_table_of_contents(soup: BeautifulSoup) -> List[Dict[str, str]]:
    toc_list = []
    toc = soup.find('div', {'id': 'toc'})
    if toc:
        for li in toc.find_all('li'):
            link = li.find('a')
            if link and 'href' in link.attrs:
                toc_list.append({
                    "title": link.get_text(strip=True),
                    "anchor": link['href']
                })
    return toc_list

def extract_sections(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    sections = []
    content = soup.select_one('#mw-content-text .mw-parser-output')
    if content:
        current_section = None
        for element in content.find_all(['h2', 'h3', 'h4', 'p', 'ul', 'ol']):
            if element.name in ['h2', 'h3', 'h4']:
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "heading": element.get_text(strip=True),
                    "content": ""
                }
            elif current_section and element.name in ['p', 'ul', 'ol']:
                current_section['content'] += element.get_text(strip=True) + "\n"
        if current_section:
            sections.append(current_section)
    return sections

def extract_images(soup: BeautifulSoup) -> List[Dict[str, str]]:
    images = []
    for img in soup.select('.mw-parser-output img'):
        src = img.get('src')
        if src:
            full_url = urljoin('https:', src)
            caption = img.get('alt', '')
            images.append({"url": full_url, "caption": caption})
    return images

def extract_tables(soup: BeautifulSoup) -> List[str]:
    tables = []
    for table in soup.find_all('table'):
        tables.append(str(table))
    return tables

def extract_references(soup: BeautifulSoup) -> List[str]:
    references = []
    ref_list = soup.find_all('li', id=re.compile('^cite_note'))
    for ref in ref_list:
        references.append(ref.get_text(strip=True))
    return references

def extract_categories(soup: BeautifulSoup) -> List[str]:
    categories = []
    cat_div = soup.find('div', id='mw-normal-catlinks')
    if cat_div:
        for link in cat_div.find_all('a')[1:]:
            categories.append(link.get_text(strip=True))
    return categories

def extract_external_links(soup: BeautifulSoup) -> List[Dict[str, str]]:
    links = []
    ext_links = soup.select('#mw-content-text a[href^="http"]')
    for link in ext_links:
        href = link.get('href')
        text = link.get_text(strip=True)
        if href and text:
            links.append({"text": text, "url": href})
    return links

def extract_related_pages(soup: BeautifulSoup) -> List[Dict[str, str]]:
    related = []
    for link in soup.select('#mw-content-text a[href^="/wiki/"]'):
        href = link.get('href')
        if ':' not in href:
            full_url = urljoin('https://en.wikipedia.org', href)
            related.append({"title": link.get_text(strip=True), "url": full_url})
    return related

def extract_coordinates(soup: BeautifulSoup) -> Dict[str, str]:
    coords = {}
    coord_span = soup.find('span', class_='geo')
    if coord_span:
        coords["value"] = coord_span.get_text(strip=True)
    return coords

def extract_language_links(soup: BeautifulSoup) -> List[Dict[str, str]]:
    languages = []
    lang_links = soup.select('#p-lang li.interlanguage-link a')
    for link in lang_links:
        languages.append({
            "language": link.get('title'),
            "url": link.get('href')
        })
    return languages

def extract_special_data(soup: BeautifulSoup, page_type: str, infobox_data: Dict[str, Any], sections: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {}

def generate_summary(introduction: str, sections: List[Dict[str, Any]], page_type: str) -> str:
    return introduction[:300] + '...'

def extract_lists(soup: BeautifulSoup) -> List[str]:
    lists = []
    for ul in soup.select('.mw-parser-output ul'):
        lists.append(ul.get_text(strip=True))
    return lists

def extract_disambiguation(soup: BeautifulSoup) -> List[str]:
    notes = []
    for div in soup.select('.hatnote'):
        notes.append(div.get_text(strip=True))
    return notes

def extract_taxonomic_data(soup: BeautifulSoup) -> Dict[str, str]:
    taxonomy = {}
    for row in soup.select('table[class*="infobox"] tr'):
        header = row.find('th')
        data = row.find('td')
        if header and data:
            key = header.get_text(strip=True)
            val = data.get_text(strip=True)
            if key and val:
                taxonomy[key] = val
    return taxonomy

def extract_media(soup: BeautifulSoup) -> List[str]:
    media = []
    for audio in soup.find_all('audio'):
        source = audio.find('source')
        if source and source.get('src'):
            media.append(urljoin('https:', source['src']))
    return media

def extract_page_stats(soup: BeautifulSoup) -> Dict[str, Any]:
    stats = {}
    # Optional: Count elements for fun stats
    stats["paragraph_count"] = len(soup.find_all('p'))
    stats["image_count"] = len(soup.find_all('img'))
    stats["section_count"] = len(soup.find_all(['h2', 'h3']))
    return stats

def extract_population_info(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    """Extract population information for place pages."""
    population_info = {}
    
    # Get the text content
    text = data_cell.get_text(strip=True)
    
    # Try to extract the number
    number_match = re.search(r'([\d,]+)', text)
    if number_match:
        try:
            population_info['count'] = int(number_match.group(1).replace(',', ''))
        except ValueError:
            population_info['count'] = number_match.group(1)
    
    # Try to extract the year
    year_match = re.search(r'\((\d{4})\)', text)
    if year_match:
        population_info['year'] = int(year_match.group(1))
    
    # Store in infobox data if we found anything
    if population_info:
        infobox_data[label] = population_info

def extract_area_info(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    """Extract area information for place pages."""
    area_info = {}
    
    # Get the text content
    text = data_cell.get_text(strip=True)
    
    # Try to extract the number and unit
    area_match = re.search(r'([\d,.]+)\s*(km²|sq\s*km|square\s*kilometers?|mi²|square\s*miles?)', text, re.IGNORECASE)
    if area_match:
        try:
            area_info['value'] = float(area_match.group(1).replace(',', ''))
        except ValueError:
            area_info['value'] = area_match.group(1)
        area_info['unit'] = area_match.group(2).strip()
    
    # Store in infobox data if we found anything
    if area_info:
        infobox_data[label] = area_info

def extract_location_info(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    """Extract location information."""
    location_info = {}
    
    # Try to find coordinates
    coords = data_cell.find('span', class_=['geo', 'coordinates'])
    if coords:
        coord_text = coords.get_text(strip=True)
        coord_match = re.search(r'([-\d.]+)[°\s]*[NS][;\s]*([-\d.]+)[°\s]*[EW]', coord_text)
        if coord_match:
            location_info['coordinates'] = {
                'latitude': float(coord_match.group(1)),
                'longitude': float(coord_match.group(2))
            }
    
    # Extract location name from links
    links = data_cell.find_all('a')
    if links:
        location_parts = []
        for link in links:
            link_text = link.get_text(strip=True)
            if link_text:
                location_parts.append({
                    'name': link_text,
                    'url': urljoin('https://en.wikipedia.org', link.get('href', ''))
                })
        if location_parts:
            location_info['parts'] = location_parts
    
    # If no structured data found, use plain text
    if not location_info:
        text = data_cell.get_text(strip=True)
        if text:
            location_info['text'] = text
    
    # Store in infobox data if we found anything
    if location_info:
        infobox_data[label] = location_info

def extract_administrative_info(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    """Extract administrative division information."""
    admin_info = {}
    
    # Try to find links first
    links = data_cell.find_all('a')
    if links:
        admin_parts = []
        for link in links:
            link_text = link.get_text(strip=True)
            if link_text:
                admin_parts.append({
                    'name': link_text,
                    'url': urljoin('https://en.wikipedia.org', link.get('href', ''))
                })
        if admin_parts:
            admin_info['parts'] = admin_parts
    
    # If no links found, use plain text
    if not admin_info:
        text = data_cell.get_text(strip=True)
        if text:
            admin_info['text'] = text
    
    # Store in infobox data if we found anything
    if admin_info:
        infobox_data[label] = admin_info

def extract_date_info(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    """Extract date information."""
    date_info = {}
    
    # Try to find specific date spans
    date_span = data_cell.find('span', class_=['bday', 'date'])
    if date_span:
        date_info['date'] = date_span.get_text(strip=True)
    
    # If no specific span, try to extract from text
    if not date_info:
        text = data_cell.get_text(strip=True)
        # Look for common date formats
        date_patterns = [
            r'(\d{1,2}\s+\w+\s+\d{4})',  # 25 December 2000
            r'(\w+\s+\d{1,2},\s+\d{4})',  # December 25, 2000
            r'(\d{4})',  # Just year
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                date_info['date'] = match.group(1)
                break
    
    # Store in infobox data if we found anything
    if date_info:
        infobox_data[label] = date_info

def extract_people_info(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    """Extract information about people (leaders, key people, etc.)."""
    people_info = []
    
    # Try to find all person links
    links = data_cell.find_all('a')
    for link in links:
        link_text = link.get_text(strip=True)
        if link_text:
            person = {
                'name': link_text,
                'url': urljoin('https://en.wikipedia.org', link.get('href', ''))
            }
            # Look for role in text near the link
            parent = link.parent
            if parent:
                full_text = parent.get_text(strip=True)
                role_match = re.search(rf'{re.escape(link_text)}\s*\(([^)]+)\)', full_text)
                if role_match:
                    person['role'] = role_match.group(1)
            people_info.append(person)
    
    # If no links found but there's text, store as plain text
    if not people_info:
        text = data_cell.get_text(strip=True)
        if text:
            people_info = text
    
    # Store in infobox data if we found anything
    if people_info:
        infobox_data[label] = people_info

def extract_participants_info(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    """Extract information about participants (for events, conflicts, etc.)."""
    participants = []
    
    # Look for participant groups (often in separate divs or list items)
    groups = data_cell.find_all(['div', 'li'])
    if groups:
        for group in groups:
            group_info = {}
            
            # Extract links within the group
            links = group.find_all('a')
            if links:
                group_info['members'] = []
                for link in links:
                    link_text = link.get_text(strip=True)
                    if link_text:
                        group_info['members'].append({
                            'name': link_text,
                            'url': urljoin('https://en.wikipedia.org', link.get('href', ''))
                        })
            
            # Extract any flags or symbols
            flags = group.find_all('img')
            if flags:
                group_info['flags'] = []
                for flag in flags:
                    if 'src' in flag.attrs:
                        group_info['flags'].append({
                            'src': flag['src'] if flag['src'].startswith('http') else f"https:{flag['src']}",
                            'alt': flag.get('alt', '')
                        })
            
            # If we found any info, add the group
            if group_info:
                participants.append(group_info)
    
    # If no structured data found, use plain text
    if not participants:
        text = data_cell.get_text(strip=True)
        if text:
            participants = text.split('\n')
    
    # Store in infobox data if we found anything
    if participants:
        infobox_data[label] = participants

def extract_taxonomic_field(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    """Extract taxonomic classification information."""
    tax_info = {}
    
    # Try to find links first
    links = data_cell.find_all('a')
    if links:
        tax_info['name'] = links[0].get_text(strip=True)
        tax_info['url'] = urljoin('https://en.wikipedia.org', links[0].get('href', ''))
        
        # Look for additional information in italics (often scientific names)
        italic = data_cell.find('i')
        if italic:
            tax_info['scientific_name'] = italic.get_text(strip=True)
    
    # If no links found, use plain text
    if not tax_info:
        text = data_cell.get_text(strip=True)
        if text:
            tax_info['name'] = text
    
    # Store in infobox data if we found anything
    if tax_info:
        infobox_data[label] = tax_info

def extract_website_info(data_cell: BeautifulSoup, infobox_data: Dict[str, Any], label: str):
    """Extract website information."""
    website_info = {}
    
    # Try to find external links
    links = data_cell.find_all('a', class_='external')
    if links:
        website_info['url'] = links[0].get('href', '')
        website_info['text'] = links[0].get_text(strip=True)
    else:
        # Try any link
        links = data_cell.find_all('a')
        if links:
            website_info['url'] = links[0].get('href', '')
            website_info['text'] = links[0].get_text(strip=True)
    
    # If no links found but there's text that looks like a URL
    if not website_info:
        text = data_cell.get_text(strip=True)
        if re.match(r'https?://', text):
            website_info['url'] = text
    
    # Store in infobox data if we found anything
    if website_info:
        infobox_data[label] = website_info
