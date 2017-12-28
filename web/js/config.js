$(function() {
	$.getJSON("http://localhost:5049/api/v1/dev?callback=?", function (devs) {
		for (var i = 0; i < devs.length; i++) {
			var item = $('<li><span class="text"></span><table></table></li>');
			$.getJSON("http://localhost:5049/api/v1/dev/" + devs[i] + "/name?callback=?", function (name) {
				item.children(".text").text(name);
			});
			for (var j = 0; j < inputs.length; j++) {
				var row = $("<tr></tr>");
				row.append("<td>" + inputs[i].displayName + "</td>");
				row.append('<td><input name="' + name + '" /></td>');
				button = $("<button></button>");
				button.click(function () {
					$(this).parent().parent().find('input[name="' + inputs[i].name + '"]')
				});
			}
			item.children("table").ap
			item.data("dev", devs[i]);
			item.click(function () {
				$(this).children(".expanding").show()
			});
			$("#devList").append(item);
		}
	});
});

var inputs = [
	{
		displayName: "Name",
		name: "name",
		url: "name",
	}
];