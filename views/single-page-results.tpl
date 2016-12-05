<!DOCTYPE html>
<html>
	<head>
		<title>Results - Web Search Engine Crawly Thingamajigger</title>
		<meta charset="utf-8">
		<link rel="stylesheet" type="text/css" href="/static/style.css">
		<link rel="stylesheet" type="text/css" href="/static/results.css">
		<link href="https://fonts.googleapis.com/css?family=Roboto:400,700" rel="stylesheet">
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
		<script src="https://www.gstatic.com/charts/loader.js"></script>
	</head>
	<body>
		<main>
			<h1><a href="http://{{ domain + path }}" title="External Link">{{ domain + path }}</a></h1>
			<p>That didn't take so long, did it?</p>
			<p>Go back to the <a href="/results/{{ domain }}">main results page</a>, or <a href="/">start over</a>.</p>
			<h3>General Information</h3>
			<table id="general-info">
				<tr>
					<td>Title</td>
					<td>{{ title }}</td>
				</tr>
				<tr>
					<td>Language</td>
					<td>{{ lang }}</td>
				</tr>
				<tr>
					<td>Number of Words</td>
					<td>{{ num_of_words }}</td>
				</tr>
				<tr>
					<td>Avg. Word Length</td>
					<td>{{ avg_word_len }} letters</td>
				</tr>
				<tr>
					<td>Encoding</td>
					<td>{{ encoding }}</td>
				</tr>
				<tr>
					<td>Internal Links</td>
					<td>{{ num_of_internal_links }}</td>
				</tr>
				<tr>
					<td>External Links</td>
					<td>{{ num_of_external_links }}</td>
				</tr>
				<tr>
					<td>Broken Links</td>
					<td>{{ num_of_broken_links }}</td>
				</tr>
			</table>
			<h3>Background Colors</h3>
			<div class="color-container">
				% for color in background_colors:
					<div style="background-color:#{{ color }}"></div>
				%end
			</div>
			<h3>Font Colors</h3>
			<div class="color-container">
				% for color in font_colors:
					<div style="background-color:#{{ color }}"></div>
				%end
			</div>
			<div id="chart">

			</div>
		</main>
		<script>
			google.charts.load('current', {'packages': ['corechart']});
			google.charts.setOnLoadCallback(drawChart);

			function drawChart() {
				var data = new google.visualization.DataTable();
				data.addColumn('string', 'Element');
				data.addColumn('number', '#');
				data.addRows([
					% for e in elements:
						["{{ e['name'] }}", {{ e['number'] }}],
					%end
				]);

				var options = {
					'title': 'Element Distribution',
					'height': 500
				};

				var chart = new google.visualization.BarChart(document.getElementById('chart'));

				chart.draw(data, options);
			}
		</script>
	</body>
</html>