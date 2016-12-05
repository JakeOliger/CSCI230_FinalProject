<!DOCTYPE html>
<html>
	<head>
		<title>Results - Web Search Engine Crawly Thingamajigger</title>
		<meta charset="utf-8">
		<link rel="stylesheet" type="text/css" href="/static/style.css">
		<link rel="stylesheet" type="text/css" href="/static/results.css">
		<link href="https://fonts.googleapis.com/css?family=Roboto:400,700" rel="stylesheet">
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
	</head>
	<body>
		<main>
			<h1><a href="http://{{ domain }}" title="External Link">{{ domain }}</a></h1>
			<p>That didn't take so long, did it?</p>
			<p><a href="/">Click here to start over.</a></p>
			<h3>General Info</h3>
			<table id="general-info">
				<tr>
					<td>Server</td>
					<td>{{ server }}</td>
				</tr>
				<tr>
					<td>Server-side Scripting Language</td>
					<td>{{ serverside_lang }}</td>
				</tr>
				<tr>
					<td>Pages Found</td>
					<td>{{ num_of_pages }}</td>
				</tr>
				<tr>
					<td>Uses jQuery?</td>
					<td>{{ uses_jquery }}</td>
				</tr>
				<tr>
					<td>SSL Support?</td>
					<td>{{ ssl_support }}</td>
				</tr>
				<tr>
					<td>Has robots.txt File?</td>
					<td>{{ has_robotstxt }}</td>
				</tr>
				<tr>
					<td>Has CSRF Protection?</td>
					<td>{{ csrf_protection }}</td>
				</tr>
			</table>
			<h3>Pages Found</h3>
			<p>Click for page-specific information</p>
			<div id="pages">
				% for page in pages:
					<a href="{{ domain + page['path'] }}" title="{{ page['path'] }}">{{ page['title'] }}</a>
				% end
			</div>
		</main>
	</body>
</html>