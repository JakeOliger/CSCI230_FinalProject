# Built in
import re
import sqlite3

# Third party
from bs4 import BeautifulSoup
import requests

class Page:
	def __init__(self, parent, path, linked_from='', depth=0):

		# The site object
		self.parent = parent

		# Used to determine if the page succeeds in being processed
		self.broken = False

		# If there have been more than 100 pages logged, quit
		if self.parent.tentativePageCount > 100:
			self.broken = False
			return
		else:
			self.parent.tentativePageCount += 1

		# Stuff that we'll be sending to the DB
		self.path = path
		self.linked_from = linked_from
		self.depth = depth
		self.encoding = ""
		self.lang = ""
		self.title = ""
		self.num_of_words = 0
		self.avg_word_len = 0
		self.num_of_broken_links = 0
		self.background_colors = ""
		self.font_colors = ""
		self.num_of_internal_links = 0
		self.num_of_external_links = 0
		self.num_of_stylesheets = 0
		self.num_of_script = 0
		self.num_of_div = 0
		self.num_of_p = 0
		self.num_of_span = 0
		self.num_of_img = 0
		self.num_of_a = 0
		self.num_of_html5_container = 0
		self.num_of_form = 0
		self.num_of_list = 0
		self.num_of_table = 0
		self.num_of_video = 0
		self.num_of_audio = 0
		self.num_of_canvas = 0
		self.num_of_input = 0
		self.num_of_button = 0

		if self.path[0:1] != '/':
			self.path = '/' + self.path

		print("STARTING: " + self.path + " (" + str(self.parent.tentativePageCount) + ")")
		
		try:
			user_agent = {'User-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36"}
			req = requests.get(parent.url + self.path, headers=user_agent)
		except requests.exceptions.ConnectionError as e:
			print(e)
			self.broken = True
			self.parent.tentativePageCount -= 1
			return

		print(' --> ' + str(req.status_code))

		if req.status_code >= 400:
			self.broken = True
			self.parent.tentativePageCount -= 1
			return

		self.encoding = req.encoding

		soup = BeautifulSoup(req.content, 'html.parser')

		if soup.html == None:
			self.parent.tentativePageCount -= 1
			self.broken = False
			return


		if 'lang' in soup.html.attrs:
			self.lang = soup.html.attrs['lang']

		if soup.title:
			self.title = soup.title.string
		
		# Element statistics
		self.num_of_script = len(soup.find_all('script'))
		self.num_of_stylesheets = len(soup.find_all('style') + soup.find_all('link', type='text/css'))
		self.num_of_div = len(soup.find_all('div'))
		self.num_of_p = len(soup.find_all('p'))
		self.num_of_span = len(soup.find_all('span'))
		self.num_of_img = len(soup.find_all('img'))
		self.num_of_a = len(soup.find_all('a'))
		self.num_of_html5_container = len(soup.find_all(['main', 'nav', 'footer', 'header', 'article', 'section']))
		self.num_of_form = len(soup.find_all('form'))
		self.num_of_list = len(soup.find_all(['ul', 'ol']))
		self.num_of_table = len(soup.find_all('table'))
		self.num_of_video = len(soup.find_all('video'))
		self.num_of_audio = len(soup.find_all('audio'))
		self.num_of_canvas = len(soup.find_all('canvas'))
		self.num_of_input = len(soup.find_all('input'))
		self.num_of_button = len(soup.find_all('button'))

		# Get the colors
		self.getColors(soup)
		
		# Get the word metricsy stuff
		self.getWordMetrics(soup)

		# Now for the recursive bit...
		self.getAllLinkedPages(soup)

		# We're done, so add us to the database
		self.addPageToDatabase('scraper.db')

	# Determines background colors and font colors used on the site
	def getColors(self, soup):
		# Find all the stylesheets
		stylesheets = []

		styleTags = soup.find_all('style')
		linkTags = soup.find_all('link', type='text/css')

		for i in styleTags:
			stylesheets.append(str(i.string))

		for i in linkTags:
			if 'href' in i.attrs:
				requestPath = ''
				if 'http' in i.attrs['href']:
					# Handle external stylesheets
					requestPath = i.attrs['href']
				else:
					if '/' == i.attrs['href'][0:1]:
						# Handle absolute paths
						requestPath = self.parent.url + i.attrs['href']
					else:
						# Handle relative paths
						requestPath = self.parent.url + self.path + i.attrs['href']
				styleReq = None
				try:
					styleReq = requests.get(requestPath, timeout=3)
				except requests.exceptions.Timeout as e:
					print(e)
				if styleReq:
					stylesheets.append(str(styleReq.content))

		# Find the colors by singling out each rule in the CSS files
		fontColors = []
		backgroundColors = []
		for i in stylesheets:
			rules = re.findall('[a-zA-Z\-]+ *: *[^;\{\}]+;', i)
			for j in rules:
				j = j.lower()
				colors = re.findall('(#[a-fA-F0-9]{6}|#[a-fA-F0-9]{3})', j)
				if j.startswith('background-color'):
					backgroundColors += colors
				elif j.startswith('color'):
					fontColors += colors# All the colors, don't bother with the hashtags

		self.background_colors = ','.join(set(backgroundColors)).replace('#', '')
		self.font_colors = ','.join(set(fontColors)).replace('#', '')

	# Determines number of words and average word length for the page
	def getWordMetrics(self, soup):
		# Determine the number of words and average length of the word
		textContainingElements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'])

		words = []

		for i in textContainingElements:
			text = i.get_text()
			if text != None and text != '':
				text = re.sub(' +', ' ', text)
				text = re.sub('\n', '', text)
				words += [x for x in text.split(' ') if x != '']

		words = [re.sub('[^a-zA-Z0-9\-]', '', x) for x in words]

		self.num_of_words = len(words)
		if self.num_of_words > 0:
			self.avg_word_len = round(len(''.join(words)) / self.num_of_words, 3)
		else:
			self.avg_word_len = 0

	# Gets all linked internal pages and creates Page instances for them
	def getAllLinkedPages(self, soup):
		links = soup.find_all('a')
		for a in links:
			if 'href' in a.attrs:
				path = a.attrs['href']

				# Skip mailto links
				if path.lower().startswith(('mailto:', 'tel:', 'callto:')):
					continue

				# If the link references the site (e.g. jakeoliger.com having a link
				# that's "https://jakeoliger.com/projects" instead of "/projects"),
				# remove the self-reference
				if self.parent.url in path:
					path = path.replace(self.parent.url, '')

				# Metrics
				if 'http' in path:
					self.num_of_external_links += 1
				else:
					self.num_of_internal_links += 1

				# Handle relative links better
				if path.startswith('./'):
					path = path[2:]

				levelsBack = 0
				while path.startswith('../'):
					levelsBack += 1
					path = path[3:]

				if levelsBack > 0:
					splitPath = self.path.split('/')
					path = '/'.join(splitPath[:len(splitPath) - levelsBack]) + path

				# Ensure it's as clean as we can reasonably get it
				if path.find('?') != -1:
					path = path[0:path.find('?')]
				if path.find('#') != -1:
					path = path[0:path.find('#')]
				if path == '':
					continue
				if path[-1] == '/' and path != '/':
					path = path[:-1]

				# Ensure external links and pages already visited aren't visited again
				if 'http' in path or path in self.parent.pages:
					continue

				self.parent.pages.append(path)

				p = Page(self.parent, path, self.path, self.depth + 1)
				if p.broken:
					self.num_of_broken_links += 1

	# Connect to database, insert site
	# Bohemoth of a function right now because of formatting the SQL statements
	# Should look into a cleaner solution for this.
	def addPageToDatabase(self, database):
		conn = sqlite3.connect(database)
		c = conn.cursor()

		c.execute("SELECT * FROM pages WHERE site_id=? AND path=?", (self.parent.site_id, self.path))

		if c.fetchone() == None:
			c.execute('''INSERT INTO pages (
				site_id,
				path,
				linked_from,
				encoding,
				lang,
				title,
				num_of_words,
				avg_word_len,
				background_colors,
				font_colors,
				num_of_internal_links,
				num_of_external_links,
				num_of_broken_links,
				num_of_stylesheets,
				num_of_script,
				num_of_div,
				num_of_p,
				num_of_span,
				num_of_img,
				num_of_a,
				num_of_html5_container,
				num_of_form,
				num_of_list,
				num_of_table,
				num_of_video,
				num_of_audio,
				num_of_canvas,
				num_of_input,
				num_of_button,
				depth)
				 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
				(
					self.parent.site_id,
					self.path,
					self.linked_from,
					self.encoding,
					self.lang,
					self.title,
					self.num_of_words,
					self.avg_word_len,
					self.background_colors,
					self.font_colors,
					self.num_of_internal_links,
					self.num_of_external_links,
					self.num_of_broken_links,
					self.num_of_stylesheets,
					self.num_of_script,
					self.num_of_div,
					self.num_of_p,
					self.num_of_span,
					self.num_of_img,
					self.num_of_a,
					self.num_of_html5_container,
					self.num_of_form,
					self.num_of_list,
					self.num_of_table,
					self.num_of_video,
					self.num_of_audio,
					self.num_of_canvas,
					self.num_of_input,
					self.num_of_button,
					self.depth
				)
			)
		else:
			c.execute('''UPDATE pages SET
				linked_from=?,
				encoding=?,
				lang=?,
				title=?,
				num_of_words=?,
				avg_word_len=?,
				background_colors=?,
				font_colors=?,
				num_of_internal_links=?,
				num_of_external_links=?,
				num_of_broken_links=?,
				num_of_stylesheets=?,
				num_of_script=?,
				num_of_div=?,
				num_of_p=?,
				num_of_span=?,
				num_of_img=?,
				num_of_a=?,
				num_of_html5_container=?,
				num_of_form=?,
				num_of_list=?,
				num_of_table=?,
				num_of_video=?,
				num_of_audio=?,
				num_of_canvas=?,
				num_of_input=?,
				num_of_button=?,
				depth=?
				WHERE site_id=? AND path=?''',
				(
					self.linked_from,
					self.encoding,
					self.lang,
					self.title,
					self.num_of_words,
					self.avg_word_len,
					self.background_colors,
					self.font_colors,
					self.num_of_internal_links,
					self.num_of_external_links,
					self.num_of_broken_links,
					self.num_of_stylesheets,
					self.num_of_script,
					self.num_of_div,
					self.num_of_p,
					self.num_of_span,
					self.num_of_img,
					self.num_of_a,
					self.num_of_html5_container,
					self.num_of_form,
					self.num_of_list,
					self.num_of_table,
					self.num_of_video,
					self.num_of_audio,
					self.num_of_canvas,
					self.num_of_input,
					self.num_of_button,
					self.depth,
					self.parent.site_id,
					self.path
				)
			)

		conn.commit()
		conn.close()