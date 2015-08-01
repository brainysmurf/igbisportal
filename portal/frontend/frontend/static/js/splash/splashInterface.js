(function (Splash) {

Splash.editModeHandler = function (e) {
  (e || window.event).returnValue = "It looks like you are in edit mode.";
  return "You can save changes or continue and lose the changes you made.";
}

Splash.changeMade = function () {
	window.addEventListener("beforeunload", Splash.editModeHandler);
	$('#editButton').text('Save Changes').css('background', '#008000').css('color', '#FFF');
	Splash.state.changeMade = true;
}

Splash.changesMade = function () {
    window.removeEventListener("beforeunload", Splash.editModeHandler);
    Splash.state.changeMade = false;
}

Splash.defineTriggers = function () {

	$('body').on('click', 'a:not(.ui-tabs-anchor)', function (e) {
		if (localStorage.getItem(Splash.config.openInNewWindowKey) === '1') {
			e.preventDefault();
			window.open($(e.target).attr('href'), '_blank');
		}

		// let the default behaviour happen
	});

	$('#newButtonButton').attr('disabled', true);
	$('#newTabButton').attr('disabled', true);
	$(".slideOnModify").animate({width:'toggle'},350);

	//Every time we click on a tab, update interface, and also save for future reference

	$('#tabs_titlebar').on('click', '.draggableTab', function (e) {
		var index = $(Splash.tabs.tabsSelector).tabs('option', 'active');
	  	localStorage.setItem(Splash.config.currentTabKey, index.toString());

		if (Splash.state.isEditing) {
			var tab = Splash.tabs.getCurrentTab();
			if (tab.kind == 'systemTab') {
				$('#newButtonButton').prop('disabled', true);
			} else {
				$('#newButtonButton').prop('disabled', false);
			}
		}

	});

	// settings dialog box
	$("#new_tab_checkbox").change(function () {
	  var value = $(this).val();
	  value = value == "1" ? "0" : "1";
	  localStorage.setItem(Splash.config.openInNewWindowKey, value);
	  $(this).val(value);

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

	$('#newButtonButton').on('click', function (e) {

		e.preventDefault();
		$('#nbd_name').val("");
		$('#nbd_link').val("");

		Splash.newEditButtonDialog(e);

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

						// FIXME:
						$tabs.tabs({active: -1});
						var index = $(Splash.tabs.tabsSelector).tabs('option', 'active');
					  	localStorage.setItem(Splash.config.currentTabKey, index.toString());

					    $(this).dialog('close');
					}
				}
 			    Splash.changeMade();
			  }
			}
		});

		e.preventDefault();

	});

	$('#tabs_holder').on('click', '.deleteOnButton', function (e) {	
		e.preventDefault();
		e.stopPropagation();

		var $parent = $(e.target).parent();
		var button = Splash.tabs.getButton($parent);
		$(button.idSelector).css('display', 'none');   // delete from the DOM
		Splash.tabs.getCurrentTab().buttons.splice(button.position-1, 1);
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

		console.log('here');

		var size;
		var $parent = $(e.target).parent();

		$parent.toggleClass('large');
		var button = Splash.tabs.getButtonById($parent.data('id'));
		button.size = $parent.hasClass('large') ? "large" : "";

		if ($parent.hasClass('large')) {
			size = 220;
		} else {
			size = 100;
		}
		$parent.data('width', size);
		$parent.data('height', size);
		$('.gridly').gridly('layout');
	});

  var savedEditingText = $('#editButton').html();
  $('#editButton').on('click', function (e) {
    var obj = $(this);
    e.preventDefault();

	$(".slideOnModify").animate({width:'toggle'}, 350);

    if (Splash.state.isEditing) {

      // It's on, turn it off
      // Update to the server
      // Restore to original state
	  $('#editButton').html(savedEditingText);

	  // ensure the new button and new tab are disabled
	  $('#newButtonButton').prop('disabled', true);
	  $('#newTabButton').prop('disabled', true);

      // Check for dirty flags, ajax updates to the server, re-enable button on success with success message
      // on failure, report offline status to the user.
      if (Splash.state.changeMade) {
      	  var savedText = $('#editButton').html();
   		  $('#editButton').prop('disabled', true);
    	  $('#editButton').html('<i class="fa fa-clock-o"></i>&nbsp;Saving...');
    	  var serialized = JSON.stringify(Splash.tabs.tabs);

    	  localStorage.setItem(Splash.config.localStorageKey, serialized);

    	  // This sends all the tab and button information
    	  // The server handles all the logic of detecting new buttons, etc.

		  $.ajax({
		    type:'PUT',
		    url: 'updateButtons',
		    contentType: 'application/json; charset=utf-8',
		    data: JSON.stringify(Splash.tabs.tabs),
		    complete: function (ignore, ignoreToo) {
		    	setTimeout(function () {
		    		$('#editButton').html(savedText);
		    		$('#editButton').prop('disabled', false);
		    	}, 1500);
		    },
		    success: function(result) {
		    	// just echoes at the moment
		    	console.log(result);
		    	setTimeout(function () {
		    		$('#editButton').html('<span style="color:#008000;"><i class="fa fa-thumbs-up"></i>&nbsp;Success!</span>');
		    	}, 500);
		    }
		  });

        Splash.changesMade();
      } else {
		//nothing special
      }

      obj.removeAttr('style');

      // This stuff makes the buttons appear as normal again
      // TODO: Implement as trigger instead
      $('.buttonContainer').removeClass('editButton');
      $('.buttonContainer').find('*').removeClass('editButton');
      $('.buttonContainer').find('*:not(.onButton)').animate({opacity: 1});
      $('.buttonContainer').removeClass('noBorder');
      $('.onButton').animate({opacity:0});

      // Make the tabs normal again too
      $('#tabs_titlebar').find('li').removeClass('editTab');
      $('#tabs_titlebar').sortable('destroy');

      // Make the buttons clickable again!
      $('.buttonContainer').find('*:not(.onButton)').removeClass('js-avoidClicks');

      // Enable the pop-ups and tell the grid to not to allow dragging
      Splash.tabs.enableJBoxes();
      $('.grid').gridly('draggable', 'off');
      Splash.state.isEditing = false;

    } else if (!Splash.state.isEditing) {

      // It's off, turn it on

   	  $('#newTabButton').prop('disabled', false);
   	  $('#editButton').text('No changes');
      var currentTab = Splash.tabs.getCurrentTab();
      // Looking at the tab, 
      // FIXME: Don't rely on the names!
      if (currentTab.kind == 'systemTab') {
      		// ensure the new button and new tab are disabled
      		$('#newButtonButton').prop('disabled', true);
      } else {
      		$('#newButtonButton').prop('disabled', false);
      }

      obj.css('border-color', '#008000');

      // Disable the pop-ups
      Splash.tabs.disableJBoxes();

     // Make the button transition to editable state
     $('.buttonContainer:not(.systemButton)').addClass('editButton');
     $('.buttonContainer:not(.systemButton').find('*').addClass('editButton');
     $('.buttonContainer').find('*:not(.onButton)').animate({opacity: 0.4});
     $('.buttonContainer').addClass('noBorder');
     $('.buttonContainer.systemButton > .onButton').css('display', 'none');
     $('.buttonContainer:not(.systemButton) > .onButton').animate({opacity: 1}, {
          done: function () {
              $('.buttonContainer').find('*:not(.onButton)').addClass('js-avoidClicks');
          },
      });
     $('#tabs_titlebar').addClass('editTab');
     $('#tabs_titlebar').sortable(Splash.config.sortable);

      $('.grid:not(.systemTab)' ).gridly('draggable', 'on');
      Splash.state.isEditing = true;
    }
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
},

Splash.newEditButtonDialog = function (event) {
	var isOnButton = $(event.target).hasClass('onButton');
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

	    	// if (Splash.utils.isValidURL($('#nbd_link').val())) {
		    // 	$done.prop("disabled", false).removeClass("ui-state-disabled");
	    	// } else {
		    // 	$done.prop("disabled", true).addClass("ui-state-disabled");
		    // }
	    	$('#newButtonDialog').find('.js-validate-msg').text('');

		   	$("#newButtonDialog").keyup(function(e) {
	    		var name = $('#nbd_name').val();
	    		var link = $('#nbd_link').val();

	    		if (name && link) {
			    	// Validate link
			    	if (Splash.utils.isValidURL(link)) {
						//$done.prop("disabled", false).removeClass("ui-state-disabled");
						$('#newButtonDialog').find('.js-validate-msg').text("");
			    	} else {
			    		//$done.prop("disabled", true).addClass("ui-state-disabled");
						$('#newButtonDialog').find('.js-validate-msg').text('Invalid URL');
			    	}
				}
		    	if (e.keyCode == $.ui.keyCode.ENTER) {
		        	$done.click();
	    		}
	    		// else if (name == "" && link == "") {
    			// 	$done.prop("disabled", true).addClass("ui-state-disabled");
	    		// }
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

				 Splash.changeMade();

			    $(this).dialog('close');
			}
		  }
		}
	});
}

}(this.Splash));