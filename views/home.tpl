<!DOCTYPE html>
<html>
	<head>
		<title>Web Search Engine Crawly Thingamajigger</title>
		<meta charset="utf-8">
		<link rel="stylesheet" type="text/css" href="/static/style.css">
		<link href="https://fonts.googleapis.com/css?family=Roboto:400,700" rel="stylesheet">
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
	</head>
	<body>
		<main>
			<h1>Website Analyzerinator</h1>
			<p>All of your info are belong to us</p>
			<input id="website" type="text" placeholder="Website to analyzinate...">
			<p id="hint">press "Enter" to continue...</p>
			<div id="spinner-container">
				<div id="spinner-container-inner">
					<div id="spinner-container-inner-inner">
						<div id="spinner">
							<div>
								<p>Loading...</p>
							</div>
						</div>
					</div>
				</div>
			</div>
			<div id="initialResponseData">
				<p>Initial response data</p>
				<table>
					<tr>
						<td>Interpreted URL</td>
						<td id="interpretedURL"></td>
					</tr>
					<tr>
						<td>Redirected URL</td>
						<td id="redirectedURL"></td>
					</tr>
					<tr>
						<td>Status</td>
						<td id="status"></td>
					</tr>
					<tr>
						<td>Response time</td>
						<td id="responseTime"></td>
					</tr>
					<tr>
						<td>Encoding</td>
						<td id="encoding"></td>
					</tr>
					<tr>
						<td>Headers</td>
						<td>
							<table id="headers">
								
							</table>
						</td>
					</tr>
				</table>
			</div>
		</main>
		<script>
			var serverTimeAtRequestReceived = 0;
			var targetSite = "";

			$('input').click(function() {
				$('#hint').slideDown(250);
			});

			$(window).keydown(function(e) {
				if (e.key === 'Enter' || e.keyCode === 13 || e.which === 13) {
					var oneFinished = false;
					$('#website, #hint').slideUp(250, function() {
						if (!oneFinished) {
							$('#spinner-container').slideDown();
							$.ajax({
								'type': 'POST',
								'url': '/analyzinate',
								'data': {'website': document.getElementById('website').value},
								'dataType': 'JSON',
								'complete': function(response, status) {
									response = response.responseJSON;

									serverTimeAtRequestReceived = response['current_time'];

									var intervalId = setInterval(function() {
										// Keep checking for updated info...
										$.ajax({
											'type': 'POST',
											'url': '/check-on-progress',
											'data': {'website': targetSite},
											'dataType': 'JSON',
											'complete': function(response, status) {
												response = response.responseJSON;

												if (response['last_updated'] > serverTimeAtRequestReceived) {
													clearInterval(intervalId);
													$('#spinner-container').slideUp(250, function() {
														window.location.href = "http://localhost:8080/results/" + response['domain'];
													});
												}
											}
										});
									}, 5000);

									targetSite = response['url'];

									// Update the table thing to appease the user while we do the real work
									document.getElementById('interpretedURL').innerHTML = response['interpreted_url'];
									document.getElementById('redirectedURL').innerHTML = response['url'];
									document.getElementById('status').innerHTML = response['status'];
									document.getElementById('responseTime').innerHTML = response['response_time_ms'] + " ms";
									document.getElementById('encoding').innerHTML = response['encoding'];
									var headers = document.getElementById('headers');
									for (var i in response['headers']) {
										var tr = document.createElement('TR');
										var key = document.createElement('TD');
										var value = document.createElement('TD');

										key.innerHTML = i;
										value.innerHTML = response['headers'][i];

										tr.appendChild(key);
										tr.appendChild(value);

										headers.appendChild(tr);
									}
									$('#initialResponseData').slideDown(250);
								}
							})
						}
						oneFinished = true;
					});
				}
			});
		</script>
	</body>
</html>