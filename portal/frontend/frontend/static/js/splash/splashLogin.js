(function (Splash) {
'use strict';

$("#edit_button").bootstrapSwitch({
  onText: 'On',
  offText: '',
  labelWidth: 80,
  labelText: '<i class="fa fa-edit"></i>&nbsp;Edit Mode',
  onColor: 'success',
  size: 'mini', 
  inverse: true,
  onSwitchChange: function (event, state) {
    $containers = $('.splash_button_container');

    if (state) {  // edit mode on

      // enable drag'n'drop
      $.each($containers, function (index, value) {
        var $buttons = $(value).find('.splash_button_item');
          $(value).packery('bindUIDraggableEvents', $buttons);
        $buttons.draggable('enable');
        $buttons.find('.splash_button > a').css('cursor', 'move');  // specificity gets rid of a:-webkit-any-link definition
        $splash_button_texts = $buttons.find('.splash_button_text');
        $splash_button_texts.css('cursor', 'text');
        $splash_button_texts.addClass('editable');
      });
    } else {      // edit mode off

      $.each($containers, function (index, value) {
        var $buttons = $(value).find('.splash_button_item');
        $buttons.draggable('disable');
        $buttons.find('.splash_button > a').css('cursor', 'pointer');
        $splash_button_texts = $buttons.find('.splash_button_text');
        $splash_button_texts.removeClass('editable');
        $splash_button_texts.css('cursor', 'pointer');
      });


    }

  }
});

function do_settings_dialog() {

  $('#settingsButton').on('click', function () {

    // TODO: Enable and disable jboxes here
    $('#settings_dialog').dialog({
      dialogClass: "no-close",
      resizeable: false,
      hide: "fold",
      show: "fold",
      model: true,
      title: "Settings",
      height: 250,
      width: 400,
      close: false,
      buttons: {
        "Done": function () { 
          $(this).dialog('close');
        }
      }
    });
  });
}

var unique = $('#unique').data('unique');

if (unique === "") {
  do_settings_dialog();
  $('#button_list').attr('style', 'display:block;');
}

}(this.Splash));