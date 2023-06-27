$("#id_branch").change(function () {
  var url = $("#profileUpdateForm").attr("branch-url"); // get the url of the `load_cities` view
  var branchID = $(this).val(); // get the selected country ID from the HTML input

  $.ajax({
    url: url,

    data: {
      branch: branchID,
    },
    success: function (data) {
      // `data` is the return of the `load_cities` view function
      $("#id_branch").html(data); // replace the contents of the city input with the data that came from the server
    },
  });
});

$("#id_college").change(function () {
  var url = $("#profileUpdateForm").attr("college-url"); // get the url of the `load_cities` view
  var collegeID = $(this).val(); // get the selected country ID from the HTML input

  $.ajax({
    url: url,

    data: {
      college: collegeID,
    },
    success: function (data) {
      // `data` is the return of the `load_cities` view function
      $("#id_college").html(data); // replace the contents of the city input with the data that came from the server
    },
  });
});

$("#id_city").change(function () {
  var url = $("#myAwesomeForm").attr("city-url"); // get the url of the `load_cities` view
  var cityID = $(this).val(); // get the selected country ID from the HTML input

  $.ajax({
    url: url,

    data: {
      city: cityID,
    },
    success: function (data) {
      // `data` is the return of the `load_cities` view function
      $("#id_city").html(data); // replace the contents of the city input with the data that came from the server
    },
  });
});
