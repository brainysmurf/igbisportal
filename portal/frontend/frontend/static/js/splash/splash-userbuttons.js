function isValidURL(url)
{
    try {
        var uri = new URI(url);
        // URI has a scheme and a host
        return (!!uri.scheme() && !!uri.host());
    }
    catch (e) {
        // Malformed URI
        return false;
    }
}

$('#newBlah').on('click', function (e) {
	e.preventDefault();
});

$('a[href="#+').on('click', function (e) {

	$('#newTabDialog').dialog({
	    dialogClass: "no-close",
		resizeable: false,
		hide: "fade",
		show: "fade",
		model: true,
		title: "Create New Tab",
		height: 150,
		width: 400,
	    open: function () {
	    	var $done = $("#newTabDialog").parent().find(":button:contains('Done')");
	    	$("#newTabDialog > input").val('');
	    	$done.prop("disabled", true).addClass("ui-state-disabled");

		   	$("#newTabDialog").keyup(function(e) {
				$done.prop("disabled", false).removeClass("ui-state-disabled");
		    	if (e.keyCode == $.ui.keyCode.ENTER) {
		        	$done.click();
	    		}
	    		else if ($(e.target).val() == "") {
    				$done.prop("disabled", true).addClass("ui-state-disabled");
	    		}
    		});
    	},
		close: false,
		buttons: {
		  "Cancel": function () {
		  	$(this).dialog('close');
		  },
		  "Done": function () {

			var $tabs = $('#tabs_holder');
		  	var newTabName = $('#ntd_from').val();
		  	var newTabNameIndex = newTabName.replace(/ /g, '_');
		  	var index = $('#tabs_holder a[href="#'+ newTabNameIndex + '"]').parent().index();

		  	if (newTabName) {
		  		if (index != -1) { 
		  			alert('Tab name have to be unique!');
		  		} else {
					var nextToLastLi = $tabs.find('ul > li:nth-last-child(2)');

				  	// TODO: Add target depending on user setting? to be consistent?
				  	var newTabTitle = $('<li><a href="#'+ newTabNameIndex + '">' + newTabName + '</a></li>');
				  	nextToLastLi.after(newTabTitle);

				  	var $newButton = $('#newButtonHolder').children().clone();
				  	$newButton.removeAttr('style');

				  	newTab = $('<div id="' + newTabNameIndex + '"></div>');
				  	newTab.prepend($newButton);

				  	var $nextToLastDiv = $tabs.children('div:nth-last-child(2)');
				  	$nextToLastDiv.after(newTab);

				  	$tabs.tabs("refresh");
				  	var index = $('#tabs_holder a[href="#'+ newTabNameIndex + '"]').parent().index();
				  	$tabs.tabs('option', 'active', index);

				    $(this).dialog('close');

				  	$newButton.find('a').click();
				}
			}
		  }
		}
	});

	e.preventDefault();

});

$('#tabs_holder').on('click', '.newButton', function (e) {

	$('#newButtonDialog').dialog({
	    dialogClass: "no-close",
		resizeable: false,
		hide: "fade",
		show: "fade",
		model: true,
		title: "New Button",
		height: 300,
		width: 400,
		close: false,
	    open: function () {
	    	var $done = $("#newButtonDialog").parent().find(":button:contains('Done')");
			$("#newButtonDialog > input").val('');

	    	$done.prop("disabled", true).addClass("ui-state-disabled");
		   	$("#newButtonDialog").keyup(function(e) {
	    		var name = $('#nbd_name').val();
	    		var link = $('#nbd_link').val();

	    		if (name && link) {
			    	// Validate link
			    	if (isValidURL(link)) {
						$done.prop("disabled", false).removeClass("ui-state-disabled");
						$('#newButtonDialog').find('.js-validate-msg').text("");
			    	} else {
			    		$done.prop("disabled", true).addClass("ui-state-disabled");
						$('#newButtonDialog').find('.js-validate-msg').text('Invalid URL');
			    	}
				}
		    	if (e.keyCode == $.ui.keyCode.ENTER) {
		        	$done.click();
	    		}
	    		else if (name == "" && link == "") {
    				$done.prop("disabled", true).addClass("ui-state-disabled");
	    		}
    		})
    	},
		buttons: {
		  "Cancel": function () {
		  	$(this).dialog('close');
		  },
		  "Done": function () { 
			var $tabs = $('#tabs_holder');
		  	var $newButton = $('#newButtonHolder').children().clone();
	    	var $done = $("#newButtonDialog").parent().find(":button:contains('Done')");
	    	if (!$done.hasClass('ui-state-disabled')) {

		    	var name = $('#nbd_name').val();
		    	var link = $('#nbd_link').val();
		    	$newButton.find('a').find('span').text(name);
		    	$newButton.removeAttr('style');

		    	$newButton.find('a').removeClass('newButton').attr('href', link);

			  	index = $tabs.tabs('option', 'active');
			  	$currentTab = $tabs.children('div div:nth-child('+ (index + 2).toString() + ')');
			  	$currentTab.append($newButton);

			    $(this).dialog('close');
			}
		  }
		}
	});

	e.preventDefault();

});
