var unique = $('#unique').data('unique');
if (unique === "") {
  do_settings_dialog();
  do_update();
  $('#button_list').attr('style', 'display:block;');
}

$('#tabs_holder').tabs();

$('.buttons_for_jbox').each(function () {

  var jbox = this.jBox('Tooltip', {
      position: {
          y: 'top',
      },
      outside: 'x',
      title: '<a href="'+ $(this).data('url') + '"><i class="fa fa-'+ $(this).data('icon') + ' fa-fw"></i>&nbsp;' + $(this).data('name') + '</a>',
      closeOnMouseleave:true,
      content: $('#submenus_for_${another_counter}')
  });

  jbox_array.push(jbox);

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