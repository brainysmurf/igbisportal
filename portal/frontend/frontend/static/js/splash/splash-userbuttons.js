
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
				  	var newTabTitle = $('<li><a class="draggableTab" href="#'+ newTabNameIndex + '">' + newTabName + '</a></li>');
				  	lastLi.after(newTabTitle);

				  	$newTab = $('#newTabHolder').children().clone();
				  	$newTab.attr('id', newTabNameIndex);

				  	var $lastDiv = $tabs.children('div:last-child');
				  	$lastDiv.after($newTab);

				  	$tabs.tabs("refresh");
				  	var index = $('#tabs_holder a[href="#'+ newTabNameIndex + '"]').parent().index();
				  	$tabs.tabs('option', 'active', index);
					$newTab.find('.grid').gridly(Splash.config.gridly);

					$('#newButtonButton').attr('disabled', false);
				    $(this).dialog('close');
				}
			}
		  }
		}
	});

	e.preventDefault();

});




}

