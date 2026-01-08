from bs4 import BeautifulSoup
from typing import List, Dict, Union
import requests

def parse_faculty_from_url(url: str) -> List[Dict]:
    """
    Fetch HTML from live URL and parse faculty records.
    """
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return parse_faculty_html(resp.text)



def clean_text(s: str) -> str:
    """Normalize whitespace."""
    return " ".join(s.split())


def extract_value(body):
    texts = [
        clean_text(t)
        for t in body.stripped_strings
        if clean_text(t) and clean_text(t) not in {"·", "●", "•"}
    ]

    if len(texts) > 1:
        return texts

    text = texts[0] if texts else ""
    if "·" in text:
        return [t.strip() for t in text.split("·") if t.strip()]

    return text


def parse_faculty_modal(modal) -> Dict:
    """
    Parse a single faculty modal div into structured dict.
    """
    faculty = {}

    # -------- BASIC INFO --------
    name_tag = modal.select_one(".name h2")
    if name_tag:
        faculty["name"] = clean_text(name_tag.text)

    for li in modal.select(".Fa-list li"):
        label = li.select_one("span")
        if not label:
            continue

        key = clean_text(label.text).lower().replace(" ", "_")
        value = clean_text(
            li.get_text(" ", strip=True).replace(label.text, "")
        )

        faculty[key] = value or None

    # -------- ACCORDION SECTIONS --------
    for item in modal.select(".accordion-item"):
        header = item.select_one(".accordion-button")
        body = item.select_one(".accordion-body")

        if not header or not body:
            continue

        key = clean_text(header.text).lower().replace(" ", "_")
        faculty[key] = extract_value(body)

    return faculty


def parse_faculty_html(html: str) -> List[Dict]:
    """
    Parse full HTML page and return list of faculty records.
    """
    soup = BeautifulSoup(html, "html.parser")
    faculty_list = []

    for modal in soup.select("div.modal"):
        faculty = parse_faculty_modal(modal)
        if faculty:
            faculty_list.append(faculty)

    return faculty_list


def parse_faculty_html_file(path: str) -> List[Dict]:
    """
    Convenience wrapper for file-based parsing.
    """
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    return parse_faculty_html(html)
