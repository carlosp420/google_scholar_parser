import urllib2;
import re;
import string;
import sys;
from BeautifulSoup import BeautifulSoup;


if len(sys.argv) < 2:
	print "enter as argument a google scholar citation link";
	print "example: http://scholar.google.com/scholar?oi=bibs&hl=en&cites=108642523785399070";
	sys.exit();

# example URL
#parse from Scielo
#url = "http://scholar.google.com/scholar?oi=bibs&hl=en&cites=108642523785399070";

url = sys.argv[1].strip();

url += "&num=1000";

UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'

req = urllib2.Request(url=url,
					headers={'User-Agent':UA});

f = urllib2.urlopen(req);

# scrape html page
# test doc.
#html_file = open("a.html","r");
#html_doc = html_file.read();
#html_file.close();

html_doc = f.read();
soup = BeautifulSoup(html_doc);


## 

#------------------------------------------------------------------------------
# @input: "soup" object obtained from one pace of Google Scholar cites
# eg.: http://scholar.google.com/scholar?oi=bibs&hl=en&cites=108642523785399070
# @output: links containing identifiers of citations (eg. DOI);
def parse_soup_page(soup):
	for div in soup.findAll('div'):
		if div.name == "div" and div.get('class') == "gs_ri":
			link = div.a['href'];
			parse_link(link);

#------------------------------------------------------------------------------
# @input: string URL or paper link begining with http://
# @output: DOI or other identifier. eg. doi: 10.10....
#			other: http://xxxyyyyzzz
def parse_link(link):
	pattern = "(10\.[0-9]{3,}[\.\d+]*\/(?![\"&'<>])\S+)";
	matches = re.search(pattern, link, re.UNICODE)
	if matches:
		doi = matches.groups()[0].strip();
		doi = re.sub("\/full$", "", doi);
		print doi;


#--------------------------------------------------
# Do something
parse_soup_page(soup);

