(function (Splash) {

Splash.defineExtentions = function () {
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
          if (result.data[i].name != null) {
            link_list += '<li><a href="' + result.data[i].link + '">&nbsp;' + result.data[i].name + '</a></li>';
          }
        }
        $('#mb_classes').parent().replaceWith(link_list);
      }
    }
  });

}

}(this.Splash));