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

function do_update() {
  
  var value = $("#new_tab_checkbox").val();
  if (value == "1") {
    $('a').each(function(index, element) {
      $(this).attr('target', '_blank_'+index);
    });
  }


  $.ajax({
    type:'POST',
    url: 'mb_homeroom',
    contentType: 'application/json; charset=utf-8',
    success: function(result) {
      if (result.hasOwnProperty('data') && result.data.length > 0) {
        var link_list = '<li><hr /></li><li class="buttonSubHeading">Email teachers of:</li>';
        for (var i=0; i < result.data.length; i++) {
          link_list += '<li><a href="mailto:' + result.data[i].student_email + '">&nbsp;' + result.data[i].student_name + '</a></li>';
        }
        $('#mb_homeroom').parent().replaceWith(link_list);
      }
    }
  });

  $.ajax({
    type:'POST',
    url: 'mb_grade_teachers',
    contentType: 'application/json; charset=utf-8',
    success: function(result) {
      if (result.hasOwnProperty('data') && result.data.length > 0) {
        var link_list = '<li><hr /></li><li class="buttonSubHeading">Email teachers of:</li>';
        for (var i=0; i < result.data.length; i++) {
          link_list += '<li><a href="mailto:' + result.data[i].teacher_emails + '">&nbsp; Grade ' + result.data[i].grade + '</a></li>';
        }
      }
      $('#mb_grade_teachers').parent().replaceWith(link_list);
    }
  });

  $.ajax({
    type:'POST',
    url: 'mb_courses',
    contentType: 'application/json; charset=utf-8',
    success: function(result) {
      if (result.hasOwnProperty('data') && result.data.length > 0) {
        var link_list = '<li><hr /></li><li class="buttonSubHeading"></i>Your courses:</li>';
        for (var i=0; i < result.data.length; i++) {
          if (result.data[i].shortname != null) {
            link_list += '<li><a href="' + result.data[i].link + '" title="' + result.data[i].name + '">&nbsp;' + result.data[i].shortname + '</a></li>';
          }
        }
        $('#mb_classes').parent().replaceWith(link_list);
      }
    }
  });
}

var unique = $('#unique').data('unique');

if (unique === "") {
  do_settings_dialog();
  do_update();
  $('#button_list').attr('style', 'display:block;');
}

}(this.Splash));