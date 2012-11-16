import urllib2;
from BeautifulSoup import BeautifulSoup;


# example URL
url = "http://scholar.google.com/scholar?oi=bibs&hl=en&cites=108642523785399070";
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



#--------------------------------------------------
# @input: "soup" object obtained from one pace of Google Scholar cites
# eg.: http://scholar.google.com/scholar?oi=bibs&hl=en&cites=108642523785399070
# @output: links containing identifiers of citations (eg. DOI);
def parse_soup_page(soup):
	for div in soup.findAll('div'):
		if div.name == "div" and div.get('class') == "gs_ri":
			link = div.a['href'];
			print link;



#--------------------------------------------------
# Do something
parse_soup_page(soup);
