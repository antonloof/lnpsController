function getJson(url, context, success) {
	$.ajax({
		dataType: "json",
		url: url,
		context: context,
		success: function (resp) {
			success(resp, $(this));
		}
	});
}

function update(currentLimit, current, voltage, name, teststatus, statusDiv, dev) {
	getJson("/api/v1/dev/" + dev + "/led", statusDiv, function(data, target) {
		target.addClass("led-status-" + data);
	});
	getJson("/api/v1/dev/" + dev + "/teststatus", teststatus, function(data, target) {
		if (data != null) {
			target.text(data);
		}
	});
	getJson("/api/v1/dev/" + dev + "/name", name, function(data, target) {
		target.text(data);
	});
	// get voltage, current, currentLimit
	getJson("/api/v1/dev/" + dev + "/ps/status/voltage", voltage, function(data, target) {
		target.text(round(data, 2) + " V");
	});
	getJson("/api/v1/dev/" + dev + "/ps/status/status/current", current, function(data, target) {
		target.text(round(data, 2) + " A");
	});
	getJson("/api/v1/dev/" + dev + "/ps/status/currentLimit", currentLimit, function(data, target) {
		target.text("/ " + round(data, 2) + " A");
	});
}

$(function () {
	$.getJSON("/api/v1/dev", function(resp) {
		resp.sort();
		for (var i = 0; i < resp.length; i++) {
			var currentLimit = $('<span class="current-limit">/ ? A</span>');
			var current = $('<span class="current">? A</span>');
			var voltage = $('<span class="voltage">? V</span>');
			var name = $('<h2 class="name">?</h2>');
			var teststatus = $('<div class="test-status">?</div>')
			var statusDiv = $('<div class="status-div"></div>');
			var dev = resp[i];
			current.append(currentLimit);
			statusDiv.append(name);
			statusDiv.append(voltage);
			statusDiv.append(current);
			statusDiv.append(teststatus);
			$("body").append(statusDiv);
			update(currentLimit, current, voltage, name, teststatus, statusDiv, dev);
			setInterval(update, 60 * 1000, currentLimit, current, voltage, name, teststatus, statusDiv, dev);
		}
	});
});

function round(v, p) {
	return Math.round(v * Math.pow(10, p)) / Math.pow(10, p);
}
