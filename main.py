# Built in
import json
import sqlite3
import threading
import time
from urllib3.util.url import parse_url

# Third party
from bottle import route, run, template, static_file, request
import requests

# First party
from website import Site

# The home page route
@route('/', method='GET')
def index():
	return template('views/home.tpl')

# Route for static files like images, stylesheets, etc
@route('/static/<file>', method='GET')
def static(file):
	print(file)
	return static_file(file, root='static')

# Analyzinator route, for POSTing from the home page search feature
@route('/analyzinate', method='POST')
def analyzinate():
	target_site = request.forms.get('website')
	data = {}

	if target_site[:4] != "http":
		target_site = 'http://' + target_site

	req = None

	try:
		# Give it a bunk user agent
		user_agent = {'User-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36"}
		req = requests.get(target_site, headers=user_agent)
	except Exception as e:
		print(e)
		data['success'] = False
		data['detail'] = str(e)
		return json.dumps(data)

	data['success'] = True
	data['response_time_ms'] = req.elapsed.microseconds // 1000
	data['encoding'] = req.encoding
	data['headers'] = dict(req.headers)
	data['status'] = str(req.status_code) + " (" + req.reason + ")"
	data['url'] = req.url
	data['interpreted_url'] = target_site
	data['current_time'] = int(time.time())

	# I'm not partirace conditionscularly worried about
	thr = threading.Thread(target=startScraping, args=(req.url,))
	thr.start()

	return json.dumps(data)

# Returns the last update timestamp for the given website
@route('/check-on-progress', method='POST')
def checkOnProgress():
	target_site = request.forms.get('website')
	
	if target_site == None:
		data = {}
		data['success'] = False
		data['detail'] = "No website specified"
		return json.dumps(data)

	target_site = parse_url(target_site).host

	conn = sqlite3.connect('scraper.db')
	c = conn.cursor()
	c.execute("SELECT last_updated,domain FROM sites WHERE domain=?", (target_site,))
	fetched = c.fetchone()
	
	data = {}

	if fetched == None or fetched[0] == None:
		data['last_updated'] = -1
		data['side_id'] = -1
	else:
		data['last_updated'] = fetched[0]
		data['domain'] = fetched[1]

	data['success'] = True

	return json.dumps(data)

# Returns a results page
@route('/results/<target_site>', method='GET')
def results(target_site):
	conn = sqlite3.connect('scraper.db')
	conn.row_factory = dict_factory
	c = conn.cursor()

	# Get site info
	c.execute("SELECT * FROM sites WHERE domain=?", (target_site,))
	site_results = c.fetchone()

	if site_results == None:
		return template('views/results-failed.tpl')

	# Get the server types
	c.execute("SELECT * FROM servers")
	servers = c.fetchall()

	# Get the server side language
	c.execute("SELECT * FROM serverside_langs")
	serverside_langs = c.fetchall()

	server = "Unknown"
	for i in servers:
		if i['server_id'] == site_results['server']:
			server = i['server_name']

	serverside_lang = "Unknown"
	for i in serverside_langs:
		if i['lang_id'] == site_results['serverside_lang']:
			serverside_lang = i['lang_name']

	# Get the pages
	c.execute('SELECT path,title FROM pages WHERE site_id=?', (site_results['site_id'],))
	pages = c.fetchall()

	args = {
		'pages':           pages,
		'domain':          site_results['domain'],
		'server':          server,
		'serverside_lang': serverside_lang,
		'ssl_support':     'Yes' if site_results['ssl_support'] == 1 else 'Not forced, anyway',
		'num_of_pages':    site_results['num_of_pages'],
		'uses_jquery':     'Yes' if site_results['uses_jquery'] == 1 else 'No',
		'has_robotstxt':   'Yes' if site_results['has_robotstxt'] == 1 else 'No',
		'csrf_protection': 'Probably' if site_results['csrf_protection'] == 1 else 'Maybe'
	}

	conn.close()

	return template('views/site-results.tpl', **args)

# Returns a results page for a specific page of a site
@route('/results/<target_site>/', method='GET')
@route('/results/<target_site>/<path:re:.+>', method='GET')
def pageResults(target_site, path='/'):
	if path != '/':
		path = '/' + path

	conn = sqlite3.connect('scraper.db')
	conn.row_factory = dict_factory
	c = conn.cursor()

	# Get site id of domain
	c.execute("SELECT site_id FROM sites WHERE domain=?", (target_site,))
	site_id = c.fetchone()

	if site_id == None:
		return template('views/results-failed.tpl')

	site_id = site_id['site_id']

	# Get page info
	c.execute("SELECT * FROM pages WHERE (path=?) AND (site_id=?)", (path,site_id))
	page_results = c.fetchone()

	if page_results == None:
		return template('views/results-failed.tpl')

	# Data being passed to the template
	args = {
		'path': path,
		'domain': target_site,
		'num_of_words': page_results['num_of_words'],
		'avg_word_len': page_results['avg_word_len'],
		'encoding': page_results['encoding'],
		'title': page_results['title'],
		'lang': page_results['lang'] or "Unspecified",
		'background_colors': page_results['background_colors'].split(','),
		'font_colors': page_results['font_colors'].split(','),
		'num_of_internal_links': page_results['num_of_internal_links'],
		'num_of_external_links': page_results['num_of_external_links'],
		'num_of_broken_links': page_results['num_of_broken_links'],
		'elements': [
			{'name': 'Stylesheets', 'number': page_results['num_of_stylesheets']},
			{'name': 'Scripts', 'number': page_results['num_of_script']},
			{'name': 'Divs', 'number': page_results['num_of_div']},
			{'name': 'Paragraphs', 'number': page_results['num_of_p']},
			{'name': 'Spans', 'number': page_results['num_of_span']},
			{'name': 'Images', 'number': page_results['num_of_img']},
			{'name': 'Links', 'number': page_results['num_of_a']},
			{'name': 'HTML5 Container', 'number': page_results['num_of_html5_container']},
			{'name': 'Forms', 'number': page_results['num_of_form']},
			{'name': 'Lists', 'number': page_results['num_of_list']},
			{'name': 'Tables', 'number': page_results['num_of_table']},
			{'name': 'Videos', 'number': page_results['num_of_video']},
			{'name': 'Audios', 'number': page_results['num_of_audio']},
			{'name': 'Canvases', 'number': page_results['num_of_canvas']},
			{'name': 'Inputs', 'number': page_results['num_of_input']},
			{'name': 'Buttons', 'number': page_results['num_of_button']}
		]
	}

	return template('views/single-page-results.tpl', **args)

# Begins the scraping! Call in another thread, dis gun take a while
def startScraping(url):
	Site(url)

# Helper function shamelessly stolen from Pydocs:
# https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
# ---
# Frankly this should be built into the sqlite3 module
def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d

if __name__ == "__main__":
	run(host='localhost', port=8080, reloader=True)