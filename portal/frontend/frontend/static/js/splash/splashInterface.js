(function (Splash) {

Splash.defineTriggers = function () {
	$('#newButtonButton').attr('disabled', true);

	$('#tabs_titlebar').on('click', '.draggableTab', function (e) {
		var index = $('#tabs_holder a[href="' + $(e.target).attr('href') + '"]').parent().index();
		var howMany = $('.notUserCreated').length;
		// TODO: Count the number of those provided 
		if (index > (howMany - 1)) {
			$('#newButtonButton').attr('disabled', false);		
		}
		else {
			$('#newButtonButton').attr('disabled', true);		
		}
	});

	$('#newButtonButton').on('click', function (e) {

		e.preventDefault();
		Splash.newEditButtonDialog(e);

		// straight-forward setting
		$('#nbd_name').val("New Button");
		$('#nbd_link').val("");
		//$('#nbd_preview i').attr('class', iconInfo);

		// change both the backend and user-faceing frontend pop-up
		$("#nbd_color").val('#EEEEEE');
		$('.btn-colorselector').css('background-color', '#EEEEEE');
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
					  	var newTabTitle = $('<li><a class="draggableTab" href="#'+ newTabNameIndex + '">' + newTabName + '</a></li>');
					  	lastLi.after(newTabTitle);

					  	var $newTab = $('#newTabHolder').children().clone();
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

	$('#tabs_holder').on('click', '.editOnButton', function (e) {
		e.preventDefault();
		e.stopPropagation();

		var $parent = $(e.target).parent();
		var text = $parent.find('.buttonTitle').text();
		var link = $parent.find('a').attr('href');
		var color = $parent.css('backgroundColor');
		var iconInfo = $parent.find('.buttonIcon i').attr('class');

		// get the right color
		color = Splash.utils.hexc(color);

		// straight-forward setting
		$('#nbd_name').val(text);
		$('#nbd_link').val(link);
		//$('#nbd_preview i').attr('class', iconInfo);

		// change both the backend and user-faceing frontend pop-up
		$("#nbd_color").val(color);
		$('.btn-colorselector').css('background-color', color);

		Splash.newEditButtonDialog(e);
	});
},

Splash.newEditButtonDialog = function (event) {
	var isOnButton = $(event.target).attr('class') != 'nav_button';
	if (isOnButton) {
		var $targetButton = $(event.target).parent();
	}

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

	    	$('#nbd_name').focus();  // TODO: Why doesn't this work?

	    	$('#nbd_color').colorselector();
	    	$('#nbd_icon').iconpicker({
	    		placement: 'topRight',
	    		hideOnSelect: true,
	    	});

	    	var $done = $("#newButtonDialog").parent().find(":button:contains('Done')");

	    	if (Splash.utils.isValidURL($('#nbd_link').val())) {
		    	$done.prop("disabled", false).removeClass("ui-state-disabled");
	    	} else {
		    	$done.prop("disabled", true).addClass("ui-state-disabled");
		    }
	    	$('#newButtonDialog').find('.js-validate-msg').text('');

	    	var $preview = $('#nbd_preview');
	    	$preview.find("*").css('opacity', 1);
	    	if (isOnButton) {
				var iconInfo = $targetButton.find('i').attr('class');
				$preview.find('i').attr('class', iconInfo);
				$preview.find('.buttonTitle').text($('#nbd_name').val());
				$('#nbd_icon').val(iconInfo);
				$('#nbd_icon').parent().find('.input-group-addon > i').attr('class', iconInfo);
				$preview.find('.buttonContainer').css('background-color', $('#nbd_color').val());
	    	} else {
		    	$preview.find('i').attr('class', $('#nbd_icon').val()).addClass('fa');
		    }
	    	$preview.on('click', function(e) {
	    		e.preventDefault();
	    	});
	    	$preview.css('display', 'block');

	    	$('#nbd_icon').on('iconpickerSelected', function (e) {
	    		$preview.find('i').removeAttr('class').addClass('fa').addClass('fa-'+e.iconpickerValue);
	    	});

	    	$('#nbd_color').on('change', function (e) {
	    		var color = $('#nbd_color').val();
	    		$preview.find('.buttonContainer').css('background-color', color);
	    	});

	    	$('#nbd_name').keyup(function () {
	    		$preview.find('.buttonTitle').text($('#nbd_name').val());
	    	});

		   	$("#newButtonDialog").keyup(function(e) {
	    		var name = $('#nbd_name').val();
	    		var link = $('#nbd_link').val();

	    		if (name && link) {
			    	// Validate link
			    	if (Splash.utils.isValidURL(link)) {
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
	    	var $done = $("#newButtonDialog").parent().find(":button:contains('Done')");
	    	if (!$done.hasClass('ui-state-disabled')) {

		    	var name = $('#nbd_name').val();
		    	var link = $('#nbd_link').val();
		    	var color = $('#nbd_color').val();
		    	var icon = $('#nbd_icon').val();

		    	if (isOnButton) {
		    		$targetButton.find('.buttonTitle').text(name);
		    		$targetButton.find('a').attr('href', link);
		    		$targetButton.css('background-color', color);
		    		$targetButton.find('.buttonIcon i').attr('class', icon).addClass('fa');
		    	} else {
				  	var $newButton = $('#newButtonHolder').children().clone();
					var $tabs = $('#tabs_holder');

			    	$newButton.find('.buttonTitle').text(name);
			    	$newButton.removeAttr('style');

			    	$newButton.find('a').removeClass('newButton').attr('href', link);
			    	$newButton.css('background-color', color);
			    	$newButton.find('.buttonIcon i').removeClass('fa-plus-circle').addClass(icon);

				  	var index = $tabs.tabs('option', 'active');
				  	var $currentTab = $tabs.children('div div:nth-child('+ (index + 2).toString() + ')');

				  	$currentTab.find('.grid').append($newButton);
				  	$currentTab.find('.grid').gridly();

				 }

			    $(this).dialog('close');
			}
		  }
		}
	});
}

}(this.Splash));