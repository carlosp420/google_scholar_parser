import re
import sys
import time
import random

from BeautifulSoup import BeautifulSoup
import requests


UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'


def parse_soup_page(soup):
    """
    :param soup: object obtained from page of Google Scholar cites
                 eg.: http://scholar.google.com/scholar?oi=bibs&hl=en&cites=108642523785399070
    :return: links containing identifiers of citations (eg. DOI)
    """
    links = list()
    for div in soup.findAll('div'):
        if div.name == "div" and div.get('class') == "gs_ri":
            link = div.a['href']
            parsed_link = parse_link(link)
            if parsed_link == "no-match":
                print("Couldn't parse link:\t{0}".format(link))
            else:
                print("DOI:\t{0}".format(parsed_link))
                links.append(parsed_link)
    return links


def parse_link(link):
    """
    :param link:  string URL or paper link begining with http://
    :return: DOI or other identifier. eg. doi: 10.10....
             other: http://xxxyyyyzzz
    """
    pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)"
    matches = re.search(pattern, link, re.UNICODE)
    if matches:
        doi = matches.groups()[0].strip()
        doi = re.sub("\/full$", "", doi)
        doi = re.sub("\/abstract$", "", doi)
        doi = re.sub("\/summary$", "", doi)
        if doi:
            return doi

    # it might be from biomedcentral
    pattern = "www\.biomedcentral\.com"
    matches = re.search(pattern, link, re.UNICODE)
    if matches:
        doi = parse_biomedcentral(link)
        if doi:
            return doi

    # it might be from Zootaxa, not dois before 2013
    pattern = "www\.mapress\.com\/zootaxa"
    matches = re.search(pattern, link, re.UNICODE)
    if matches:
        doi = link
        if doi:
            return doi

    # it might be from sciencedirect
    pattern = "www\.sciencedirect\.com"
    matches = re.search(pattern, link, re.UNICODE)
    if matches:
        doi = parse_sciencedirect(link)
        if doi:
            return doi

    # it might be from royal society rspb
    pattern = "rspb\.royalsocietypublishing\.org"
    matches = re.search(pattern, link, re.UNICODE)
    if matches:
        doi = parse_rspb(link)
        if doi:
            return doi

    # it might be a PDF link from springerlink
    pattern = "springerlink\.com\/.+pdf$"
    matches = re.search(pattern, link, re.UNICODE)
    if matches:
        doi = parse_springerlink_pdf(link)
        if doi:
            return doi

    # it might be from Scielo but not a link to PDF file
    pattern = "www\.scielo\..+[^pdf]$"
    matches = re.search(pattern, link, re.UNICODE)
    if matches:
        doi = parse_scielo(link)
        if doi:
            return doi

    # it might be a handle
    pattern = "\/handle\/(\d+\/\d+)"
    matches = re.search(pattern, link, re.UNICODE)
    if matches:
        doi = "http://hdl.handle.net/" + matches.groups()[0]
        return doi

    # it might be a sysbio.oxfordjournals.org early pub link
    pattern = "sysbio.oxfordjournals.org\/.+\/early\/.+\/sysbio\.(.+)\.short"
    matches = re.search(pattern, link, re.UNICODE)
    if matches:
        doi = "10.1093/sysbio/" + matches.groups()[0]
        return doi

    # couldn't find a match
    return "no-match"


def parse_scielo(link):
    """
    :param link: string URL from springerlink ending with "pdf"
    :return: DOI or other identifier. eg. doi: 10.10....
    """
    req = requests.get(link, headers={'User-Agent': UA})
    html_doc = req.text
    soup = BeautifulSoup(html_doc)

    try:
        doi = soup.find('h4', attrs={'id': 'doi'}).contents[0]
    except:
        doi = ""
    pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)"
    matches = re.search(pattern, doi, re.UNICODE)
    if matches:
        doi = matches.groups()[0].strip()
        return doi


def parse_springerlink_pdf(link):
    """
    :param link: string URL from springerlink ending with "pdf"
    :return: DOI or other identifier. eg. doi: 10.10....
    """
    req = requests.get(link, headers={'User-Agent': UA})
    html_doc = req.text
    soup = BeautifulSoup(html_doc)

    for meta in soup.findAll("meta"):
        if meta.get('name') == "citation_doi":
            doi = meta.get('content')
            pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)"
            matches = re.search(pattern, doi, re.UNICODE)
            if matches:
                doi = matches.groups()[0].strip()
                return doi


def parse_biomedcentral(link):
    """
    :param link: string URL from biomedcentral with http://
    :return: DOI or other identifier. eg. doi: 10.10....
    """
    if "pdf" in link:
        # http://www.biomedcentral.com/content/pdf/1471-2148-12-82.pdf
        # http://www.biomedcentral.com/1471-2148/12/82
        link = re.sub("content\/pdf\/", "", link)
        link = re.sub("\.pdf$", "", link)
        link = re.sub("-(\d+)-(\d+)$", "/\\1/\\2", link)

    req = requests.get(link, headers={'User-Agent': UA})
    html_doc = req.text
    soup = BeautifulSoup(html_doc)

    for meta in soup.findAll("meta"):
        if meta.get('name') == "citation_doi":
            doi = meta.get('content')
            pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)"
            matches = re.search(pattern, doi, re.UNICODE)
            if matches:
                doi = matches.groups()[0].strip()
                return doi


def parse_sciencedirect(link):
    """
    :param link: string URL from sciencedirect with http://
    :return: DOI or other identifier. eg. doi: 10.10....
    """
    if "pdf" not in link:
        req = requests.get(url=link, headers={'User-Agent': UA})
        html_doc = req.text
        soup = BeautifulSoup(html_doc)

        tag = soup.find('a',   attrs={'id': 'ddDoi'})
        try:
            doi_link = tag.get("href")
        except:
            doi_link = ""
        pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)"
        matches = re.search(pattern, doi_link, re.UNICODE)
        if matches:
            doi = matches.groups()[0].strip()
            return doi


def parse_rspb(link):
    """
    :param link: string URL from royal society rspb with http://
    :return: DOI or other identifier. eg. doi: 10.10....
    """
    if "pdf" not in link:
        req = requests.get(link, headers={'User-Agent': UA})
        html_doc = req.text
        soup = BeautifulSoup(html_doc)

        for meta in soup.findAll("meta"):
            if meta.get('name') == "DC.Identifier":
                doi = meta.get('content')
                pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)"
                matches = re.search(pattern, doi, re.UNICODE)
                if matches:
                    doi = matches.groups()[0].strip()
                    return doi


def get_total_hits(soup):
    results = soup.find('div', attrs={'id': 'gs_ab_md'}).contents[0]
    matches = re.search("About\s(\d+)\s", results)
    if matches:
        hits = matches.groups()[0]
        return hits


def get_citing_dois(cites_url):
    """
    :param cites_url:  a citation url from GoogleScholar
    :return:           a list of DOIs extracted from URLs by following the links
    """
    n = random.random() * 5
    time.sleep(n)
    print("Sleeping: {0} seconds".format(n))

    # GS seems to allow only 20 hits per page!
    cites_url += "&num=20"
    req = requests.get(cites_url, headers={'User-Agent': UA})
    html_doc = req.text
    soup = BeautifulSoup(html_doc)
    hits = get_total_hits(soup)
    print("Got a total of {0} hits".format(hits))

    if hits:
        hits = int(hits)
        index = 0
        dois = []
        while hits > 1:
            n = random.random()*2
            time.sleep(n)
            if index > 0:
                url = cites_url + "&start=" + str(index)
            else:
                url = cites_url
            index += 20
            hits -= 20

            req = requests.get(url, headers={'User-Agent': UA})
            html_doc = req.text
            soup = BeautifulSoup(html_doc)
            links = parse_soup_page(soup)
            for i in links:
                dois.append(i)
        return dois

    else:
        # just do 20 records
        req = requests.get(cites_url, headers={'User-Agent': UA})
        html_doc = req.text
        soup = BeautifulSoup(html_doc)
        return parse_soup_page(soup)


def main():
    random.seed()

    if len(sys.argv) < 2:
        print("Enter as argument a google scholar citation link")
        print("Example: http://scholar.google.com/scholar?oi=bibs&hl=en&cites=108642523785399070")
        sys.exit(1)

    cites_url = sys.argv[1].strip()
    get_citing_dois(cites_url)


if __name__ == "__main__":
    main()
