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

var jbox_array = [];

function do_settings_dialog() {

  $('#settingsButton').on('click', function () {

    jbox_array.forEach(function (item, index) { 
      //console.log(jbox_array[index]);
      //FIXME this doesn't actually work
      jbox_array[index].disable();
    });

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
          //FIXME: check for disabled first?
          jbox_array.forEach(function (item, index) {
            jbox_array[index].enable();
          });
        }
      }
    });
  });

  $('#editButton').on('click', function (e) {
    var obj = $(this);
    e.preventDefault();

    if (obj.attr('style')) {

      // It's on
      obj.removeAttr('style');

      Splash.tabs().enableJBoxes();

      $('.buttonContainer').removeClass('editButton');
      $('.buttonContainer').find('*').removeClass('editButton');
      // $('.buttonContainer').animate({opacity:1});
      $('.buttonContainer').find('*:not(.onButton)').animate({opacity: 1});
      $('.buttonContainer').removeClass('noBorder');
      $('.onButton').animate({opacity:0});
      $('#tabs_titlebar').find('li').removeClass('editTab');
      $('#tabs_titlebar').sortable('destroy');

      $('.buttonContainer').find('*:not(.onButton)').removeClass('js-avoidClicks');
      $('.grid').gridly('draggable', 'off');

    } else {

      // It's off, turn it on

      obj.css('background', '#999').css('color', '#eee');
      Splash.tabs().disableJBoxes();

     // make the buttons editable
     $('.buttonContainer').addClass('editButton');
     $('.buttonContainer').find('*').addClass('editButton');
     $('.buttonContainer').find('*:not(.onButton)').animate({opacity: 0.4});
     $('.buttonContainer').addClass('noBorder');
     $('.onButton').animate({opacity: 1}, {
          done: function () {
              $('.buttonContainer').find('*:not(.onButton)').addClass('js-avoidClicks');
          },
      });
     $('#tabs_titlebar').addClass('editTab');
     $('#tabs_titlebar').sortable({
        axis: 'x',
        cursor: 'move',
        revert: true,
        opacity: 0.5
     });

      $('.grid' ).gridly('draggable', 'on');
    }
  });

}

var unique = $('#unique').data('unique');

if (unique === "") {
  do_settings_dialog();
  $('#button_list').attr('style', 'display:block;');
}

}(this.Splash));