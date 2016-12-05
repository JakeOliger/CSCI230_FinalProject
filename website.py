# Built in
import sqlite3
import time
from urllib3.util.url import parse_url

# Third party
from bs4 import BeautifulSoup
import requests

# First party
from page import Page

class Site:
	def __init__(self, url):
		self.pages = []
		self.stylesheets = []
		self.scripts = []
		self.num_of_pages = 0
		self.num_of_levels = 0
		self.uses_wordpress = 0
		self.ssl_support = 0
		self.csrf_protection = 0
		self.uses_jquery = 0
		self.serverType = 0
		self.serverSideLang = 0
		self.has_robotstxt = 0
		self.site_id = -1
		self.tentativePageCount = 0

		self.pages.append('/')

		url_parts = parse_url(url)
		self.url = url_parts.scheme + "://" + url_parts.host
		self.url_host = url_parts.host

		print("Getting site \"{}\"...".format(self.url))
		user_agent = {'User-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36"}
		req = requests.get(self.url, headers=user_agent)
		print(" --> {}".format(req.status_code))

		soup = BeautifulSoup(req.content, 'html.parser')

		# Determine SSL support
		self.ssl_support = 1 if 'https' in self.url else 0

		# Determine if the site has CSRF protection
		self.csrf_protection = self.detectCSRFProtection(req.headers, soup, req.cookies)

		# Checks if the site uses jQuery
		self.uses_jquery = self.getUsesJquery(soup)

		# Check if a robots.txt file exists for the site
		self.has_robotstxt = self.getHasRobotsTxt(self.url)

		# Determine if the site is using Apache, Nginx, or IIS
		if 'server' in req.headers:
			self.serverType = self.getServerType(req.headers['server'])
		
		# Determine if the site is using ASP or PHP
		if 'x-powered-by' in req.headers:
			self.serverSideLang = self.getServerSideLanguage(req.headers['x-powered-by'])

		# Get the ID of the site to pass to the page
		self.site_id = self.addSiteToDatabase('scraper.db')

		# Begin recursively getting pages
		Page(self, '/')

		self.finishUp('scraper.db')

		print("Done with site.")

	# Updates the `last_updated` field and finishes up some stats like
	# number of pages that we didn't previously have
	def finishUp(self, database):
		conn = sqlite3.connect(database)
		c = conn.cursor()

		c.execute('''UPDATE sites SET
			last_updated=?,
			num_of_pages=?
			WHERE domain=?''',
			(
				int(time.time()),
				len(self.pages),
				self.url_host
			)
		)

		conn.commit()
		conn.close()

	# Connect to database, insert site
	def addSiteToDatabase(self, database):
		conn = sqlite3.connect(database)
		c = conn.cursor()
		c.execute("SELECT site_id FROM sites WHERE domain=?", (self.url_host,))

		site_id = c.fetchone()

		if site_id == None:
			c.execute('''INSERT INTO sites (
				domain,
				serverside_lang,
				server,
				has_robotstxt,
				uses_jquery,
				ssl_support,
				csrf_protection)
				VALUES (?, ?, ?, ?, ?, ?, ?)''',
				(
					self.url_host,
					self.serverSideLang,
					self.serverType,
					self.has_robotstxt,
					self.uses_jquery,
					self.ssl_support,
					self.csrf_protection
				)
			)
			# Get ID from the query
			site_id = c.lastrowid
		else:
			c.execute('''UPDATE sites SET
				serverside_lang=?,
				server=?,
				has_robotstxt=?,
				uses_jquery=?,
				ssl_support=?,
				csrf_protection=?
				WHERE domain=?''',
				(
					self.serverSideLang,
					self.serverType,
					self.has_robotstxt,
					self.uses_jquery,
					self.ssl_support,
					self.csrf_protection,
					self.url_host
				)
			)
			# Get ID from tuple since we know there are results
			site_id = site_id[0]

		conn.commit()
		conn.close()

		return site_id

	# Tries to find evidence of CSRF protection methods
	def detectCSRFProtection(self, headers, soup, cookies):
		csrfProtection = 0
		headers = dict(headers)
		cookies = cookies.get_dict()

		for key, value in headers.items():
			if 'csrf' in key.lower() or 'csrf' in value.lower():
				csrfProtection = 1

		for key, value in cookies.items():
			if 'csrf' in key.lower() or 'csrf' in value.lower():
				csrfProtection = 1

		metas = soup.find_all('meta')
		for i in metas:
			if 'csrf' in str(i).lower():
				csrfProtection = 1

		return csrfProtection

	# Detects the server type based on the "Server" response header
	def getServerType(self, header):
		serverType = 0
		header = header.lower()
		if 'apache' in header:
			serverType = 1
		elif 'nginx' in header:
			serverType = 2
		elif 'iis' in header:
			serverType = 3
		elif 'gws' in header:
			serverType = 4

		return serverType

	# Detects a server side language based on the "X-Powered-By" response header
	def getServerSideLanguage(self, header):
		serverSideLang = 0
		header = header.lower()
		if 'php' in header:
			serverSideLang = 1
		elif 'asp' in header:
			serverSideLang = 2

		return serverSideLang

	# Determines whether or not the site is using jQuery
	def getUsesJquery(self, soup):
		scripts = soup.find_all('script')
		usesJquery = 0

		for i in scripts:
			if 'src' in i.attrs:
				if 'jquery' in i.attrs['src'].lower():
					usesJquery = 1

		return usesJquery

	# Determines whether or not the site has a robots.txt file
	def getHasRobotsTxt(self, url):
		robots = requests.get(url + '/robots.txt')
		return 1 if robots.status_code == 200 else 0

if __name__ == "__main__":
	site = Site('https://jakeoliger.com/')
