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

        // disable jboxes
      $.each(jbox_array, function (index, value) {
        value.disable();
      });

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
      // jboxes enabled
      $.each(jbox_array, function (index, value) {
        value.enable();
      });

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
    obj = $(this);
    e.preventDefault();

    if (obj.attr('style')) {

      // It's on
      obj.removeAttr('style');
      jbox_array.forEach(function (item, index) { 
        //console.log(jbox_array[index]);
        //FIXME this doesn't actually work
        jbox_array[index].enable();
      });

      $('.splashButton').find('.buttonIcon').removeClass('editButton')
      $('.splashButton').animate({opacity:1});
      $('.onButton').animate({opacity: 0}, {
          done: function() {
              $('.onButton').removeAttr('style');
          }
      });
      $('#tabs_titlebar').find('li').removeClass('editTab');
      $('#tabs_titlebar').sortable('destroy');
      $('.splashButton').off('click');

    } else {

      // It's off, turn it on

      $('.splashButton').on('click', function (e) {
          e.preventDefault();
      });

      obj.css('background', '#999').css('color', '#eee');

      // disable the jboxes
      jbox_array.forEach(function (item, index) { 
        //console.log(jbox_array[index]);
        //FIXME this doesn't actually work
        jbox_array[index].disable();
      });

     // make the buttons editable
     $('.splashButton').find('.buttonIcon').addClass('editButton');
     $('.splashButton').animate({opacity: 0.4});
     $('.onButton').animate({
          opacity: 1,
      }, {
          done: function () {
              $('.onButton').css('z-index', '2');
          },
      });
     $('#tabs_titlebar').addClass('editTab');
     $('#tabs_titlebar').sortable({
        axis: 'x',
        cursor: 'move',
        revert: true,
        opacity: 0.5
     });

     console.log('turn gridly drag on Secondary');
     $('#Secondary_Teachers').find('.grid').gridly('draggable', "on");
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
        for (i=0; i < result.data.length; i++) {
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
        for (i=0; i < result.data.length; i++) {
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
        for (i=0; i < result.data.length; i++) {
          if (result.data[i].shortname != null) {
            link_list += '<li><a href="' + result.data[i].link + '" title="' + result.data[i].name + '">&nbsp;' + result.data[i].shortname + '</a></li>';
          }
        }
        $('#mb_classes').parent().replaceWith(link_list);
      }
    }
  });

}

function signInCallback(authResult) {
  delete authResult['g-oauth-window'];  // it took me forever to find this
  //http://stackoverflow.com/questions/25065194/google-sign-in-uncaught-securityerror
  // It's started happening when I serialized the entire authResult object, could just send what I need...

  if (authResult['code']) {

    // Hide the sign-in button now that the user is authorized, for example:
    
    $('#signinButton').fadeOut("slow", function () {
        do_settings_dialog();
        $('#button_list').fadeIn("slow");
      });

    unique = $('#unique').data('unique');

    $.ajax({
      type: 'POST',
      url: 'signinCallback?' + unique,
      contentType: 'application/json; charset=utf-8',
      success: function(result) {
          window.location.reload();   // refresh
          do_update();
        },
      data: JSON.stringify({'authResult':authResult, 'code':authResult['code']})
      });
  } else if (authResult['error']) {
    // There was an error.
    // Possible error codes:
    //   "access_denied" - User denied access to your app
    //   "immediate_failed" - Could not automatially log in the user
    console.log('There was an error: ' + authResult['error']);
    // do this just in case we have the user anyway
    do_update();
  }
}