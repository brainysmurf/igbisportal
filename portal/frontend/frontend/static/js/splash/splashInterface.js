(function (Splash) {

Splash.defineTriggers = function () {
	$('draggableTab').on('click', function (event, ui) {
		// Update the model to let us know which is the current tab
		// Don't override default behaviour
		Splash.tabs.currentTabId = $(event.target).attr('id');
	});

	$('#newButtonButton').attr('disabled', true);

	// settings dialog box
	$("#new_tab_checkbox").change(function () {
	  var value = $(this).val();
	  value = value == "1" ? "0" : "1";
	  $(this).val(value);

	  // TODO change this to overriding triggers and window.open(url, '_blank')
	  if (value == "1") {
	    $('a').each(function(index) {
	      $(this).attr('target', '_blank_'+index);
	    });
	  } else {
	    $('a').removeAttr('target');
	  }

	  $.ajax({
	    type:'POST',
	    url: 'user_settings',
	    contentType: 'application/json; charset=utf-8',
	    success: function(result) {
	        console.log(result);
	      },
	    data: JSON.stringify({'new_tab': value})
	  });
	});

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

		if (!Splash.newEditButtonDialogInited) {
			Splash.initNewEditButtonDialog();
		}
		$("#nbd_color").colorselector('setValue', 'default');
		$('#nbd_icon').val('external-link-square');
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
			  			Splash.tabs.addTab(newTabName);

			  			// make new tab become front, and then ensure disabled
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
		var button = Splash.tabs.getButton($parent);

		$('#nbd_name').val(button.name);
		$('#nbd_link').val(button.link);

		if (!Splash.newEditButtonDialogInited) {
			Splash.initNewEditButtonDialog();
		}
		$('#nbd_icon').val(button.icon);
		$('#nbd_color').colorselector('setValue', button.color);

		Splash.newEditButtonDialog(e);
	});

	$('#tabs_holder').on('click', '.sizeOnButton', function (e) {
		e.preventDefault();
		e.stopPropagation();

		var size;
		var $parent = $(e.target).parent().toggleClass('large');

		$parent.find('.buttonTitle').css('display', 'none').toggleClass('large');

		if ($parent.hasClass('large')) {
			size = 220;
		} else {
			size = 100;
		}
		$parent.data('width', size);
		$parent.data('height', size);
		$parent.find('.buttonTitle').removeAttr('style');
		$('.gridly').gridly('layout');
	});
},

Splash.newEditButtonDialogInited = false,

Splash.initNewEditButtonDialog = function() {
	Splash.newEditButtonDialogInited = true;
	var $preview = $('#nbd_preview');
	$('#nbd_color').colorselector({
		callback: function (value, color, title) {
	    	$preview.find('.buttonContainer').alterClass('color*', 'color'+value)
		}
	});
	$('#nbd_icon').iconpicker({
		placement: 'topRight',
		hideOnSelect: true,
	});
	$('#nbd_icon').on('iconpickerSelected', function (e) {
		$preview.find('i').alterClass('fa-*', 'fa-'+e.iconpickerValue);
		$('#nbd_icon').val(e.iconpickerValue);
	});
	$('#nbd_icon').val('external-link-square');
	$('#nbd_name').keyup(function () {
		$preview.find('.buttonTitle').text($('#nbd_name').val());
	});
	$preview.on('click', function(e) {
		e.preventDefault();
	});
	$preview.css('display', 'block');
}

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
	    	// Should only have to do some of these things once, correct?
	    	var $preview = $('#nbd_preview');
			$preview.find("*").css('opacity', 1);
	    	$preview.find('.buttonContainer').alterClass('color*', 'color'+$('#nbd_color').val())
	    	$preview.find('.buttonIcon > i').alterClass('fa-*', 'fa-'+$('#nbd_icon').val());
	    	$preview.find('.buttonTitle').text($('#nbd_name').val());

	    	var $done = $("#newButtonDialog").parent().find(":button:contains('Done')");

	    	if (Splash.utils.isValidURL($('#nbd_link').val())) {
		    	$done.prop("disabled", false).removeClass("ui-state-disabled");
	    	} else {
		    	$done.prop("disabled", true).addClass("ui-state-disabled");
		    }
	    	$('#newButtonDialog').find('.js-validate-msg').text('');

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
    		});

	    	$('#nbd_name').select();
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
		    		var button = Splash.tabs.getButton($targetButton);
		    		button.updateWithValues(name, color, link, icon);
		    	} else {
		    		Splash.tabs.addButtonToCurrentTab(name, color, link, icon);
				 }

			    $(this).dialog('close');
			}
		  }
		}
	});
}

}(this.Splash));