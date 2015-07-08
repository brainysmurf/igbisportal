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
}

function do_update() {
  // FIXME: 
  // userText = $('#userButton').html();
  // if (userText.indexOf('add_name_here') != -1) {
  //   $.ajax({
  //     type:'POST',
  //     url: 'user_data',
  //     contentType: 'application/json; charset=utf-8',
  //     success: function(result) {
  //         console.log(result);
  //         userText.replace('add_name_here', result['data']);
  //         console.log(userText);
  //         $("#userButton").replaceWith(userText);
  //       }
  //   });
  // }

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
        var link_list = '<li><hr /></li><li class="button_sub_heading"><i class="fa fa-fw"></i><i class="fa fa-fw"></i>Email teachers of:</li>';
        for (i=0; i < result.data.length; i++) {
          link_list += '<li><a href="mailto:' + result.data[i].student_email + '"><i class="fa fa-envelope"></i>&nbsp;' + result.data[i].student_name + '</a></li>';
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
        var link_list = '<li><hr /></li><li class="button_sub_heading"><i class="fa fa-fw"></i><i class="fa fa-fw"></i>Email teachers of:</li>';
        for (i=0; i < result.data.length; i++) {
          link_list += '<li><a href="mailto:' + result.data[i].teacher_emails + '"><i class="fa fa-envelope"></i>&nbsp; Grade ' + result.data[i].grade + '</a></li>';
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
        var link_list = '<li><hr /></li><li class="button_sub_heading"><i class="fa fa-fw"></i><i class="fa fa-fw"></i>Your courses:</li>';
        for (i=0; i < result.data.length; i++) {
          if (result.data[i].shortname != null) {
            link_list += '<li><a href="' + result.data[i].link + '" title="' + result.data[i].name + '"><i class="fa fa-chevron-circle-right fa-fw"></i>&nbsp;' + result.data[i].shortname + '</a></li>';
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


$("input[name=icon_size]:radio").change(function () {
  var value = $(this).val();

  if ( value == '+1' ) {
  
    $(".splash_button").toggleClass('smaller');        

  } else if ( value == '-1' ) {

    $(".splash_button").toggleClass('smaller');

  }

  $.ajax({
    type:'POST',
    url: 'user_settings',
    contentType: 'application/json; charset=utf-8',
    success: function(result) {
        console.log(result);
      },
    data: JSON.stringify({'icon_size':value})
  });
});

$("#new_tab_checkbox").change(function () {
  var value = $(this).val();
  value = value == "1" ? "0" : "1";
  $(this).val(value);

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

var unique = $('#unique').data('unique');
console.log(unique);
if (unique === "") {
  do_settings_dialog();
  do_update();
  console.log("updating...");
  $('#button_list').attr('style', 'display:block;');
}
