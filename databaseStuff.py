import sqlite3

conn = sqlite3.connect('scraper.db')

c = conn.cursor()

createNewDatabase = True

if createNewDatabase:
	c.execute('''CREATE TABLE sites
				 (site_id integer primary key, domain text, num_of_levels integer,
				  num_of_pages integer, ssl_support integer, csrf_protection integer,
				  uses_jquery integer, serverside_lang integer, server integer,
				  has_robotstxt integer, last_updated integer)''')

	c.execute('''CREATE TABLE pages
				 (page_id integer primary key, site_id integer, path text,
				 linked_from text, encoding text, lang text, title text,
				 num_of_words integer, avg_word_len real, background_colors text,
				 font_colors text, num_of_internal_links integer,
				 num_of_external_links integer, num_of_stylesheets integer,
				 num_of_script integer, num_of_div integer, num_of_p integer,
				 num_of_span integer, num_of_img integer, num_of_a integer,
				 num_of_html5_container integer, num_of_form integer,
				 num_of_list integer, num_of_table integer, num_of_video integer,
				 num_of_audio integer, num_of_canvas integer, num_of_input integer,
				 num_of_button integer, depth integer, num_of_broken_links integer)''')

	c.execute('CREATE TABLE servers (server_id integer primary key, server_name text)')
	c.execute('CREATE TABLE serverside_langs (lang_id integer primary key, lang_name text)')

	serverStatement = 'INSERT INTO servers (server_name) VALUES (?)'
	c.execute(serverStatement, ('Apache',))
	c.execute(serverStatement, ('Nginx',))
	c.execute(serverStatement, ('IIS',))
	c.execute(serverStatement, ('GWS',))

	serverLangStatement = 'INSERT INTO serverside_langs (lang_name) VALUES (?)'
	c.execute(serverLangStatement, ('PHP',))
	c.execute(serverLangStatement, ('ASP',))

	conn.commit()
else:
	c.execute('SELECT * FROM sites')
	print(c.fetchall())

conn.close()