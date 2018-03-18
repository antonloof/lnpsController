var inputs = [
	{
		displayName: "Test Status",
		name: "teststatus",
		url: "teststatus",
		keyName: "teststatus",
		noget: false
	}, {
		displayName: "Voltage",
		name: "voltage",
		url: "ps/status/voltage",
		keyName: "voltage",
		noget: false
	}, {
		displayName: "Current limit",
		name: "currentLimit",
		url: "ps/status/currentLimit",
		keyName: "currentLimit",
		noget: false
	}, {
		displayName: "Remote",
		name: "remote",
		url: "ps/status/remote",
		keyName: "remote",
		noget: false
	}, {
		displayName: "Switch",
		name: "switch",
		url: "ps/status/switch",
		keyName: "switch",
		noget: false
	}, {
		displayName: "Over Voltage",
		name: "overVoltage",
		url: "ps/status/overVoltage",
		keyName: "overVoltage",
		noget: false
	}, {
		displayName: "Over Current",
		name: "overCurrent",
		url: "ps/status/overCurrent",
		keyName: "overCurrent",
		noget: false
	}, {
		displayName: "Led",
		name: "led",
		url: "led",
		keyName: "mode",
		noget: false
	}, {
		displayName: "Query",
		name: "query",
		url: "ps/query",
		keyName: "hex",
		noget: true,
		method: "POST"
	}
];

function set(url, data, context, method, success, error) {
	$.ajax({
		url: url,
		dataType: "json",
		method: method,
		context: context,
		headers: { 
			'Accept': 'application/json',
			'Content-Type': 'application/json' 
		},
		data: JSON.stringify(data),
		success: success,
		error: error
	});
}

$(function() {
	$.getJSON("/api/v1/dev", function (devs) {
		devs.sort();
		for (var i = 0; i < devs.length; i++) {
			var item = $('<li><span class="text">' + devs[i] + '</span><table class="hidden"></table></li>');
			$("#devList").append(item);
			$.ajax({
				url: "/api/v1/dev/" + devs[i] + "/name", 
				context: item,
				dataType: "json",
				success: function (name) {
					var text = $(this).children(".text").text();
					$(this).children(".text").text(name + " (" + text + ")");
				}
			});
			
			$.ajax({
				url: "/api/v1/dev/" + devs[i] + "/pw",
				dataType: "json",
				context: {item: item, dev: devs[i]},
				success: function (pw) {
					var dev = $(this)[0].dev;
					var item = $(this)[0].item;
					for (var j = 0; j < inputs.length; j++) {
						var row = $("<tr></tr>");
						row.append("<th>" + inputs[j].displayName + "</th>");
						
						var inputtd = $('<td></td>');
						var input = $('<input name="' + inputs[j].name + '" />');
						inputtd.append(input);
						row.append(inputtd)
						
						var buttontd = $("<td></td>");
						var button = $("<button>Update</button>");
						buttontd.append(button);
						row.append(buttontd);
						if (!inputs[j].noget) {
							$.ajax({
								url: "/api/v1/dev/" + dev + "/" + inputs[j].url, 
								context: input,
								dataType: "json",
								success: function (res) {
									$(this).val(res);
								}
							});
						}
						button.click({input: inputs[j], dev: dev, pw: pw}, function (evt) {
							var value = $(this).parent().parent().find('input[name="' + evt.data.input.name + '"]').val();
							var message = $(this).parent().parent().find(".message");
							set("/api/v1/dev/" + evt.data.dev + "/" + evt.data.input.url, 
								{
									[evt.data.input.keyName]: value,
									"pw": evt.data.pw
								}, 
								message, 
								evt.data.input.method == undefined ? "PUT" : evt.data.input.method,
								function (resp) {
									$(this).removeClass("error");
									$(this).text(JSON.stringify(resp));
								}, function (jqxhr, textStatus, errorThrown) {
									$(this).addClass("error");
									$(this).text(jqxhr.responseJSON);
								}
							);
						});
						
						row.append('<td class="message"></td>')
						item.children("table").append(row);
					}
					item.children(".text").click(function () {
						$(this).parent().children("table").toggleClass("hidden")
					});
				}
			});			
		}
	});
});
