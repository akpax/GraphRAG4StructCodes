import bs4
import re
from pprint import pprint
import pathlib
import json


def process_chapter(path: pathlib.PosixPath) -> dict:
    with open(path, "r") as f:
        soup = bs4.BeautifulSoup(f,"xml")
    return process_soup(soup)



def process_soup(soup: bs4.BeautifulSoup) -> dict:
    chapter = {"headers": [],
            "items": []}
    divs = soup.select("div.viewer-section")
    for div in divs:
        # items have a content-root div w contents
        if div.select_one("div.content-root"):
            chapter["items"].append(process_item_div(div))
        else:
            chapter["headers"].append(process_header_div(div))
    return chapter

def process_header_div(div: bs4.element.Tag) -> dict:
    try:
        item = {"type": "header"}
        # Select the first 'span' with class 'content-root'
        span_content_root = div.select_one("span.content-root")
        
        # Ensure span_content_root is not a NavigableString before attempting to call .find_all()
        if isinstance(span_content_root, bs4.element.Tag):
            content = []
            # Check if there are any <i> tags directly under this span
            i_tags = span_content_root.find_all("i")
            for i_tag in i_tags:
                # Prepend their text to the content list
                content.append(i_tag.text.strip())
                i_tag.decompose()
            
            # Append the main span's text
            main_text = " ".join([text for text in span_content_root.stripped_strings])
            content.insert(0, main_text)
            # Combine all pieces of text into one string and add to item dictionary
            item["content"] = " ".join(content)
            item["id"] = find_id(item["content"])
        else:
            # Handle cases where span_content_root is not a Tag object
            item["content"] = "Content not found or not a tag"

        return item
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}



def process_item_div(div: bs4.element.Tag)-> dict:
    try:
        item = {"type": "item"}
        # Using CSS selector to adjust for the provided HTML structure
        section_number_span = div.select_one(".flex.items-center h3 a span")
        if section_number_span:
            section_number = section_number_span.text.strip()
            item["id"] = section_number
        else:
            section_number = "Number not found"
    
        
        # Assuming content is directly within the .content-root.pb-3, not as described before
        content_texts = []
        content_div = div.select_one(".content-root.pb-3")
        for element in content_div.descendants:
            if element.name in ['span'] or element.name is None:
                content_texts.append(element.text.strip())
        content_text = " ".join(content_texts)  # Join text pieces to form the full content text
        item["content"] = content_text
        item["item_references"] = find_item_references(content_text)
        item["chapter_references"] = find_chapter_references(content_text)
        return item
    except Exception as e:
        print(f"An error occurred: {e}")


def find_item_references(txt: str)-> list:
    matches = re.finditer(r"\d+(\.\d+)+", txt)
    return list(set([match.group() for match in matches]))

def find_chapter_references(txt: str) -> list:
    matches = re.finditer(r"Chapter \d+", txt)
    return list(set([match.group().removeprefix("Chapter ").strip() for match in matches]))

def find_id(txt: str) -> str:
    txt = txt.strip()
    if re.search(r"^\d+(\.\d+)+", txt) is not None:
        return re.match(r"^\d+(\.\d+)+", txt).group()
    if re.search(r"^Chapter \d+", txt) is not None:
        match = re.match(r"^Chapter \d+",txt)
        return match.group().removeprefix("Chapter ").strip()
    else:
        return None

def get_chapter_from_path(path: pathlib.PosixPath) -> str:
    name = path.stem
    match = re.search(r"ch\d+", name)
    return match.group()

if __name__ == "__main__":
    data_dir = pathlib.Path("data/ACI318-19_html")
    chapters = list(data_dir.iterdir())
    ACI_dict = {}
    for ch_path in chapters:
        print(ch_path)
        ACI_dict[get_chapter_from_path(ch_path)] = process_chapter(ch_path)
    pprint(ACI_dict["ch12"])
    out_path = pathlib.Path("data/ACI318-19_json/ACI318-19_complete.json")
    with open(out_path, "w") as f:
        json.dump(ACI_dict, f)


        
    
    
    
    
    