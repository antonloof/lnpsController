$(function() {
	$.getJSON("http://localhost:5049/api/v1/dev?callback=?", function (devs) {
		for (int i = 0; i < devs.length; i++) {
			$("#devList").append('<li>Device no: ' + devs[i] + '</li>');
		}
	});
});