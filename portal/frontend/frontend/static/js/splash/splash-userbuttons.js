function isValidURL(url)
{
    try {
        var uri = new URI(url);
        // URI has a scheme and a host
        return (!!uri.scheme() && !!uri.host());
    }
    catch (e) {
        // Malformed URI
        console.log('false');
        return false;
    }
}

$('#newBlah').on('click', function (e) {
	e.preventDefault();
});

$('#newTabButton').on('click', function (e) {

	$('#newTabDialog').dialog({
	    dialogClass: "no-close",
		resizeable: false,
		hide: "fade",
		show: "fade",
		model: true,
		title: "Create New Tab",
		height: 200,
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
					var lastLi = $tabs.find('ul > li:last-child');

				  	// TODO: Add target depending on user setting? to be consistent?
				  	var newTabTitle = $('<li><a href="#'+ newTabNameIndex + '">' + newTabName + '</a></li>');
				  	lastLi.after(newTabTitle);

				  	$newTab = $('#newTabHolder').children().clone();
				  	$newTab.attr('id', newTabNameIndex);

				  	var $lastDiv = $tabs.children('div:last-child');
				  	$lastDiv.after($newTab);

				  	$tabs.tabs("refresh");
				  	var index = $('#tabs_holder a[href="#'+ newTabNameIndex + '"]').parent().index();
				  	$tabs.tabs('option', 'active', index);
					$newTab.find('.grid').gridly({
					  base: 40,
					  gutter: 10,
					  columns: 18,
					  draggable: 'off',
					});

				    $(this).dialog('close');
				}
			}
		  }
		}
	});

	e.preventDefault();

});

$('#newButtonButton').on('click', function (e) {

	e.preventDefault();
	newEditButtonDialog();

});

$('.editOnButton').on('click', function (e) {
	e.preventDefault();
	newEditButtonDialog();
});

function newEditButtonDialog() {
	$('#newButtonDialog').dialog({
	    dialogClass: "no-close",
		resizeable: false,
		hide: "fade",
		show: "fade",
		model: true,
		title: "New Button",
		height: 500,
		width: 400,
		close: false,
	    open: function () {
	    	$('#nbd_color').colorselector();
	    	$('#nbd_icon').iconpicker({
	    		placement: 'topRight',
	    		hideOnSelect: true,
	    	});

	    	var $done = $("#newButtonDialog").parent().find(":button:contains('Done')");

	    	if (isValidURL($('#nbd_link').val())) {
		    	$done.prop("disabled", false).removeClass("ui-state-disabled");
	    	} else {
		    	$done.prop("disabled", true).addClass("ui-state-disabled");
		    }
	    	$('#newButtonDialog').find('.js-validate-msg').text('');

	    	var $preview = $('#newButtonHolder').children().clone();
	    	$preview.find('a').removeClass('newButton');
	    	$preview.find('.splashButtonTitle').text('Preview');
	    	$preview.find('i').removeClass('fa-plus-circle').addClass($('#nbd_icon').val());
	    	$preview.addClass($('#nbd_color').val());
	    	$('#nbd_preview').replaceWith($preview);
	    	$preview.attr('id', 'nbd_preview');
	    	$preview.on('click', function(e) {
	    		e.preventDefault();
	    	});
	    	$preview.css('display', 'block');

	    	$('#nbd_icon').on('iconpickerSelected', function (e) {
	    		$preview.find('i').removeAttr('class').addClass('fa').addClass('fa-'+e.iconpickerValue);
	    	});

	    	$('#nbd_color').on('change', function (e) {
	    		color = $('#nbd_color').val();
	    		$('#nbd_preview').removeAttr('class').addClass('splashButton').addClass('small').addClass(color);
	    	});

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
		    	var color = $('#nbd_color').val();
		    	var icon = $('#nbd_icon').val();

		    	$newButton.find('.splashButtonTitle').text(name);
		    	$newButton.removeAttr('style');

		    	$newButton.find('a').removeClass('newButton').attr('href', link);
		    	$newButton.addClass(color);
		    	$newButton.find('.buttonIcon > i').removeClass('fa-plus-circle').addClass(icon);

			  	index = $tabs.tabs('option', 'active');
			  	$currentTab = $tabs.children('div div:nth-child('+ (index + 2).toString() + ')');

			  	$currentTab.find('.grid').append($newButton);
			  	$currentTab.find('.grid').gridly();

			  	$('#newButtonButton').click();
			    $(this).dialog('close');
			}
		  }
		}
	});
}

