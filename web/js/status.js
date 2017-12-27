$(function () {
	$.ajax({
		url: "http://localhost:5049/api/v1/dev",
		dataType: "jsonp",
		jsonpCallback: "loadBenches"
	});
});

function loadBenches(available){
  for (var i = 0; i < available.length; i++) {
		$.getJSON("http://localhost:5049/api/v1/dev/" + available[i] + "?callback=?", function (bench) {
			$("body").append('<div class="bench">' +
				'<h2>' + bench.name + '</h2>' + 
				'<div class="ps">' +
				'	<div class="display"></div>' +
				'	<span class="voltage">U<div class="spinning"><div class="stick"></div></div></span>' +
				'	<span class="current">I<div class="spinning"><div class="stick"></div></div></span>' +
				'</div>' +
				'<span class="transfer">' + round(bench.ps.status.status.current, 2) + 'A <span class="arrow">&darr;</span> ' + round(bench.ps.status.status.voltage, 2) + 'V</span>' +
				'<div class="test success">' +
				'	<h3>A test</h3>' +
				'	<p>' + bench.teststatus + '</p>' +
				'</div>');
		});
	}
}

function round(v, p) {
	return Math.round(v * Math.pow(10, p)) / Math.pow(10, p)
}