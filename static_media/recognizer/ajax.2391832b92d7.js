$("#id_teacher").change(function () {
    var url = $("#myAwesomeForm").attr("data-attendance-url");  // get the url of the `load_cities` view
    var teacherID = $(this).val();  // get the selected country ID from the HTML input
    
    $.ajax({                       
      url: url,                    
  
  
      data: {
        'teacher': teacherID       
      },
      success: function (data) {   // `data` is the return of the `load_cities` view function
        $("#id_lecture").html(data);  // replace the contents of the city input with the data that came from the server
      }
    });
  
  });

  
  $("#id_teacher").change(function () {
    var url = $("#myAwesomeForm").attr("data-attendance-url");  // get the url of the `load_cities` view
    var teacherID = $(this).val();  // get the selected country ID from the HTML input
    
    $.ajax({                       
      url: url,                    
  
  
      data: {
        'teacher': teacherID       
      },
      success: function (data) {   // `data` is the return of the `load_cities` view function
        $("#id_lecture").html(data);  // replace the contents of the city input with the data that came from the server
      }
    });
  
  });

  
  $("#id_teacher").change(function () {
    var url = $("#myAwesomeForm").attr("data-attendance-url");  // get the url of the `load_cities` view
    var teacherID = $(this).val();  // get the selected country ID from the HTML input
    
    $.ajax({                       
      url: url,                    
  
  
      data: {
        'teacher': teacherID       
      },
      success: function (data) {   // `data` is the return of the `load_cities` view function
        $("#id_lecture").html(data);  // replace the contents of the city input with the data that came from the server
      }
    });
  
  });
  