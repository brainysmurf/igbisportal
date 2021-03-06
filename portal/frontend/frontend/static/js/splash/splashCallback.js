// Sign in has to be available ASAP upon load, so don't bother wrapping in an immediately invoking function

function signInCallback(authResult) {
  delete authResult['g-oauth-window'];  // it took me forever to find this
  //http://stackoverflow.com/questions/25065194/google-sign-in-uncaught-securityerror
  // It's started happening when I serialized the entire authResult object, could just send what I need...

  if (authResult['code']) {

    // Hide the sign-in button now that the user is authorized, for example:
    
    $('#signinButton').fadeOut("slow", function () {
        $('#button_list').fadeIn("slow");
      });

    unique = $('#unique').data('unique');

    $.ajax({
      type: 'POST',
      url: 'signinCallback?' + unique,
      contentType: 'application/json; charset=utf-8',
      success: function(result) {
          if (result.message == "HTTPForbidden") {
            $('#userButton').text('Non-IGBIS Account!');
          } else {
            window.location.reload(true);   // don't reload from cache, ugh....
          }
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
    //do_update();
  }
}
