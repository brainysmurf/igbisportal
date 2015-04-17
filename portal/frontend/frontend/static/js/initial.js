console.log('initial');
var doSettingsDialog, doUpdate;

(function (){
  var jbox_array = [];

  // var jbox = $('#jbox_button_${another_counter}').jBox('Tooltip', {
  //     position: {
  //         y: 'top',
  //     },
  //     outside: 'x',
  //     title: '<a href="${button.url}"><i class="fa fa-${button.icon} fa-fw"></i>&nbsp;${button.name}</a>',
  //     closeOnMouseleave:true,
  //     content: $('#submenus_for_${another_counter}')
  // });

  // jbox_array.push(jbox);

  doSettingsDialog = function () {

    $('#settingsButton').on('click', function () {

      jbox_array.forEach(function (item, index) { 
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
            jbox_array.forEach(function (item, index) {
              jbox_array[index].enable();
            });
          }
        }
      });


    });
  }

  doUpdate = function () {
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
    console.log("Updating");

    var value = $("#new_tab_checkbox").val();
    if (value == "1") {
      $('a').each(function(index, element) {
        $(this).attr('target', '_blank_'+index);
      });
    }
    console.log("Changing..");
    $('#bp_shareablelink').replaceWith('<a href=""><i class="fa fa-user"></i>&nbsp;Test</a>');

    $('#bp_shareablelink').on('click', function () {

      $("#shareable_link").dialog({
          resizeable: false,
          hide: "fold",
          show: "fold",
          model: true,
          title: "Make BrainPop Link for Automatic Login",
          height: 250,
          width: 400,
          close: false,
          buttons: {
            "Done": function () { 
              $(this).dialog('close');
              jbox_array.forEach(function (item, index) {
                jbox_array[index].enable();
              });
            }
          }
        });

    });

    $.ajax({
      type:'POST',
      url: 'mb_homeroom',
      contentType: 'application/json; charset=utf-8',
      success: function(result) {
        if (result.hasOwnProperty('data') && result.data.length > 0) {
          var link_list = '<li><hr /></li><li class="button_sub_heading">Email teachers of:</li>';
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
          var link_list = '<li><hr /></li><li class="button_sub_heading">Email teachers of:</li>';
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
          var link_list = '<li><hr /></li><li class="button_sub_heading">Your courses:</li>';
          for (i=0; i < result.data.length; i++) {
            if (result.data[i].shortname != null) {
              link_list += '<li><a href="' + result.data[i].link + '" title="' + result.data[i].name + '"><i class="fa fa-chevron-circle-right fa-fw"></i>&nbsp;' + result.data[i].shortname + '</a></li>';
            }
          }
          $('#mb_classes').parent().replaceWith(link_list);
        }
      }
    });

  }  // doUpdate

  // now do the standard stuff at launch

  $("#from_url").change(function () {
    var value = $(this).val();
    var new_value = value + '?user=igbisbrainpop&password=2014igbis'
    $("#to_url").val(new_value);
  });

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
        console.log(value);
        value = value == "1" ? "0" : "1";
        $(this).val(value);

        if (value == "1") {
          $('a').each(function(index) {
            $(this).attr('target', '_blank_'+index);
          });
          console.log('added target');
        } else {
          $('a').removeAttr('target');
          console.log('removed target');
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
})();