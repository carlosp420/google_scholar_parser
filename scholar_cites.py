import urllib2;
import re;
import string;
import sys;
import time;
import random;
from BeautifulSoup import BeautifulSoup;



# example URL
#parse from Scielo
#url = "http://scholar.google.com/scholar?oi=bibs&hl=en&cites=108642523785399070";

#url = sys.argv[1].strip();




## 

#------------------------------------------------------------------------------
# @input: "soup" object obtained from one pace of Google Scholar cites
# eg.: http://scholar.google.com/scholar?oi=bibs&hl=en&cites=108642523785399070
# @output: links containing identifiers of citations (eg. DOI);
def parse_soup_page(soup):
	links = list();
	for div in soup.findAll('div'):
		if div.name == "div" and div.get('class') == "gs_ri":
			link = div.a['href'];
			parsed_link = parse_link(link);
			if parsed_link == "no-match":
				print "Couldn't parse link:\t", link;
			else:
				print "DOI:\t", parsed_link;
				links.append(parsed_link);
#print "";
#j = 1;
#for i in links:
#print j, i;
#j = j + 1
#sys.exit(0);
	return links;

#------------------------------------------------------------------------------
# @input: string URL or paper link begining with http://
# @output: DOI or other identifier. eg. doi: 10.10....
#			other: http://xxxyyyyzzz
def parse_link(link):
#print "link:\t", link;
	pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)";
	matches = re.search(pattern, link, re.UNICODE)
	if matches:
		doi = matches.groups()[0].strip();
		doi = re.sub("\/full$", "", doi);
		doi = re.sub("\/abstract$", "", doi);
		doi = re.sub("\/summary$", "", doi);
		if doi:
			return doi;

	# it might be from biomedcentral
	pattern = "www\.biomedcentral\.com";
	matches = re.search(pattern, link, re.UNICODE);
	if matches:
		doi = parse_biomedcentral(link);
		if doi:
			return doi;

	# it might be from Zootaxa, not dois before 2013
	pattern = "www\.mapress\.com\/zootaxa";
	matches = re.search(pattern, link, re.UNICODE);
	if matches:
		doi = link;
		if doi:
			return doi;

	# it might be from sciencedirect
	pattern = "www\.sciencedirect\.com";
	matches = re.search(pattern, link, re.UNICODE);
	if matches:
		doi = parse_sciencedirect(link);
		if doi:
			return doi;
			
	# it might be from royal society rspb
	pattern = "rspb\.royalsocietypublishing\.org";
	matches = re.search(pattern, link, re.UNICODE);
	if matches:
		doi = parse_rspb(link);
		if doi:
			return doi;

	# it might be a PDF link from springerlink
	pattern = "springerlink\.com\/.+pdf$";
	matches = re.search(pattern, link, re.UNICODE);
	if matches:
		doi = parse_springerlink_pdf(link);
		if doi:
			return doi;

	# it might be from Scielo but not a link to PDF file
	pattern = "www\.scielo\..+[^pdf]$";
	matches = re.search(pattern, link, re.UNICODE);
	if matches:
		doi = parse_scielo(link);
		if doi:
			return doi;

	# it might be a handle
	pattern = "\/handle\/(\d+\/\d+)";
	matches = re.search(pattern, link, re.UNICODE);
	if matches:
		doi = "http://hdl.handle.net/" + matches.groups()[0];
		return doi;

	# it might be a sysbio.oxfordjournals.org early pub link
	pattern = "sysbio.oxfordjournals.org\/.+\/early\/.+\/sysbio\.(.+)\.short";
	matches = re.search(pattern, link, re.UNICODE);
	if matches:
		doi = "10.1093/sysbio/" + matches.groups()[0];
		return doi;

	# couldn't find a match
	return "no-match";




#------------------------------------------------------------------------------
# @input: string URL from springerlink ending with "pdf"
# @output: DOI or other identifier. eg. doi: 10.10....
def parse_scielo(link):
	UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'
	req = urllib2.Request(url=link, headers={'User-Agent':UA});
	f = urllib2.urlopen(req);
	html_doc = f.read();
	soup = BeautifulSoup(html_doc);

	try:
		doi = soup.find('h4', attrs={'id': 'doi'}).contents[0];
	except:
		doi = "";
	pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)";
	matches = re.search(pattern, doi, re.UNICODE)
	if matches:
#print matches.groups();
		doi = matches.groups()[0].strip();
#print "doi:\t", doi;
		return doi;


#------------------------------------------------------------------------------
# @input: string URL from springerlink ending with "pdf"
# @output: DOI or other identifier. eg. doi: 10.10....
def parse_springerlink_pdf(link):
	UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'
	req = urllib2.Request(url=link,
					headers={'User-Agent':UA});
	f = urllib2.urlopen(req);
	html_doc = f.read();
	soup = BeautifulSoup(html_doc);

	for meta in soup.findAll("meta"):
		if meta.get('name') == "citation_doi":
			doi = meta.get('content');
			pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)";
			matches = re.search(pattern, doi, re.UNICODE)
			if matches:
				doi = matches.groups()[0].strip();
				return doi;


#------------------------------------------------------------------------------
# @input: string URL from biomedcentral with http://
# @output: DOI or other identifier. eg. doi: 10.10....
def parse_biomedcentral(link):
	if "pdf" in link:
		#http://www.biomedcentral.com/content/pdf/1471-2148-12-82.pdf
		#http://www.biomedcentral.com/1471-2148/12/82
		link = re.sub("content\/pdf\/", "", link);
		link = re.sub("\.pdf$", "", link);
		link = re.sub("-(\d+)-(\d+)$", "/\\1/\\2", link);

	UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'
	req = urllib2.Request(url=link,
					headers={'User-Agent':UA});
	f = urllib2.urlopen(req);
	html_doc = f.read();
	soup = BeautifulSoup(html_doc);

	for meta in soup.findAll("meta"):
		if meta.get('name') == "citation_doi":
			doi = meta.get('content');
			pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)";
			matches = re.search(pattern, doi, re.UNICODE)
			if matches:
				doi = matches.groups()[0].strip();
				return doi;


#------------------------------------------------------------------------------
# @input: string URL from sciencedirect with http://
# @output: DOI or other identifier. eg. doi: 10.10....
def parse_sciencedirect(link):
	if "pdf" not in link:
		UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'
		req = urllib2.Request(url=link, headers={'User-Agent':UA});
		f = urllib2.urlopen(req);
		html_doc = f.read();
		soup = BeautifulSoup(html_doc);

		tag = soup.find('a',   attrs={'id': 'ddDoi'});
		try:
			doi_link = tag.get("href");
		except:
			doi_link = "";
		pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)";
		matches = re.search(pattern, doi_link, re.UNICODE)
		if matches:
			doi = matches.groups()[0].strip();
			return doi;



#------------------------------------------------------------------------------
# @input: string URL from royal society rspb with http://
# @output: DOI or other identifier. eg. doi: 10.10....
def parse_rspb(link):
	if "pdf" not in link:
		UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'
		req = urllib2.Request(url=link, headers={'User-Agent':UA});
		f = urllib2.urlopen(req);
		html_doc = f.read();
		soup = BeautifulSoup(html_doc);

		for meta in soup.findAll("meta"):
			if meta.get('name') == "DC.Identifier":
				doi = meta.get('content');
				pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)";
				matches = re.search(pattern, doi, re.UNICODE)
				if matches:
					doi = matches.groups()[0].strip();
					return doi;

def get_total_hits(soup):
	results = soup.find('div', attrs={'id': 'gs_ab_md'}).contents[0];
	matches = re.search("About\s(\d+)\s", results);
	if matches:
		hits = matches.groups()[0];
		return hits;

#--------------------------------------------------
# @input a citation url from GoogleScholar
# @output a list of dois extracted from URLs or
#			by following the links
def get_citing_dois(cites_url):
	n = random.random()*5;
	time.sleep(n);
	print "Sleeping: " + str(n) + " seconds";

	cites_url += "&num=20";
	UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'

	req = urllib2.Request(url=cites_url, headers={'User-Agent':UA});
	f = urllib2.urlopen(req);
	html_doc = f.read();
	soup = BeautifulSoup(html_doc);
	# GS seems to allow only 20 hits per page!
	hits = get_total_hits(soup);
	if hits:
		hits = int(hits);
		index = 0;
		dois = [];
		while hits > 1:
			n = random.random()*2;
			time.sleep(n);
			if index > 0:
				url = cites_url + "&start=" + str(index);
			else:
				url = cites_url;
			index = index + 20;
			hits = hits - 20;

			req = urllib2.Request(url=url, headers={'User-Agent':UA});
			f = urllib2.urlopen(req);
			html_doc = f.read();
			soup = BeautifulSoup(html_doc);
			links = parse_soup_page(soup);
			for i in links:
				dois.append(i);
#for j in dois:
#print j;
#sys.exit(0);
		return dois;
			
	else:
		# just do 20 records
		req = urllib2.Request(url=cites_url, headers={'User-Agent':UA});
		f = urllib2.urlopen(req);
		html_doc = f.read();
		soup = BeautifulSoup(html_doc);
		return parse_soup_page(soup);



def main():
	random.seed();

	if len(sys.argv) < 2:
		print "enter as argument a google scholar citation link";
		print "example: http://scholar.google.com/scholar?oi=bibs&hl=en&cites=108642523785399070";
		sys.exit();

	# example URL
	# url = "http://scholar.google.com/scholar?oi=bibs&hl=en&cites=108642523785399070";

	cites_url = sys.argv[1].strip();
	get_citing_dois(cites_url);



if __name__ == "__main__":
	main();
