
var unique = $('#unique').data('unique');
if (unique === "") {
  do_settings_dialog();
  do_update();
  $('#button_list').attr('style', 'display:block;');
}

// $('#tabs_holder').tabs();

// $(function () {
//   console.log('initing gridly');
//   $('.grid').gridly({
//     base: 40,
//     gutter: 10,
//     columns: 18,
//     draggable: 'off',
//   });
//   console.log('done initing');
// });

// $('.buttons_for_jbox').each(function () {

//   $submenu = $('.submenus_for_jbox[data-counter=' + $(this).data('counter') + ']');
//   if ($submenu.length > 0) {
//     var jbox = $(this).jBox('Tooltip', {
//         position: {
//             y: 'top',
//         },
//         delayOpen: 400,
//         outside: 'x',
//         title: '<a class="submenuTitle" href="'+ $(this).data('url') + '">&nbsp;' + $(this).data('name') + '</a>',
//         closeOnMouseleave:true,
//         content: $submenu
//     });

//     jbox_array.push(jbox);
//   }
// });

// toLiItem = function (id, icon, display) {
//   return '<li id="' + id + '"><a>&nbsp;' + display+'</a></li>';
// }

// $("#bp_link").parent().replaceWith(toLiItem('bp_link', 'user', 'Shareable Link'));
// $("#bp_link").on("click", function() {
//   $('#shareable_link_bp').dialog({
//     dialogClass: "no-close",
//     resizeable: false,
//     hide: "fold",
//     show: "fold",
//     model: true,
//     title: "BrainPop Shareable Link",
//     height: 300,
//     width: 400,
//     close: false,
//     buttons: {
//       "Done": function () { 
//         $(this).dialog('close');
//       }
//     }
//   });

//   $('#bp_from').change( function () {
//     $('#bp_to').val($('#bp_from').val());
//   });

//   setInterval(function() {
//     $('#bp_to').val($('#bp_from').val());
//   }, 500);      
// });

// $("input[name=icon_size]:radio").change(function () {
//   var value = $(this).val();
//   if ( value == '+1' ) {
  
//     $(".splashButton").removeClass('small').addClass('large');

//   } else if ( value == '-1' ) {

//     $(".splashButton").removeClass('small').addClass('large');

//   }

//   $.ajax({
//     type:'POST',
//     url: 'user_settings',
//     contentType: 'application/json; charset=utf-8',
//     success: function(result) {
//       },
//     data: JSON.stringify({'icon_size':value})
//   });
// });

// $("#new_tab_checkbox").change(function () {
//   var value = $(this).val();
//   value = value == "1" ? "0" : "1";
//   $(this).val(value);

//   if (value == "1") {
//     $('a').each(function(index) {
//       $(this).attr('target', '_blank_'+index);
//     });
//   } else {
//     $('a').removeAttr('target');
//   }

//   $.ajax({
//     type:'POST',
//     url: 'user_settings',
//     contentType: 'application/json; charset=utf-8',
//     success: function(result) {
//         console.log(result);
//       },
//     data: JSON.stringify({'new_tab': value})
//   });
// });