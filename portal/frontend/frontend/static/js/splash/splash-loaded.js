
var unique = $('#unique').data('unique');
if (unique === "") {
  do_settings_dialog();
  do_update();
  $('#button_list').attr('style', 'display:block;');
}

$('#tabs_holder').tabs();

$('.buttons_for_jbox').each(function () {

  $submenu = $('.submenus_for_jbox[data-counter=' + $(this).data('counter') + ']');
  if ($submenu.length > 0) {
    var jbox = $(this).jBox('Tooltip', {
        position: {
            y: 'top',
        },
        outside: 'x',
        title: '<a href="'+ $(this).data('url') + '"><i class="fa fa-'+ $(this).data('icon') + ' fa-fw"></i>&nbsp;' + $(this).data('name') + '</a>',
        closeOnMouseleave:true,
        content: $submenu
    });

    jbox_array.push(jbox);
  }
});

toLiItem = function (id, icon, display) {
  return '<li id="' + id + '"><a><i class="fa fa-' + icon + '"></i>&nbsp;' + display+'</a></li>';
}

$("#bp_link").parent().replaceWith(toLiItem('bp_link', 'user', 'Shareable Link'));
$("#bp_link").on("click", function() {
  $('#shareable_link_bp').dialog({
    dialogClass: "no-close",
    resizeable: false,
    hide: "fold",
    show: "fold",
    model: true,
    title: "BrainPop Shareable Link",
    height: 300,
    width: 400,
    close: false,
    buttons: {
      "Done": function () { 
        $(this).dialog('close');
      }
    }
  });

  $('#bp_from').change( function () {
    $('#bp_to').val($('#bp_from').val());
  });

  setInterval(function() {
    $('#bp_to').val($('#bp_from').val());
  }, 500);      
});

$("input[name=icon_size]:radio").change(function () {
  var value = $(this).val();
  console.log(value);
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