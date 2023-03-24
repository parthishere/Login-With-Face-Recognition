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





(function() {
    // The width and height of the captured photo. We will set the
    // width to the value defined here, but the height will be
    // calculated based on the aspect ratio of the input stream.
  
    var width = 320;    // We will scale the photo width to this
    var height = 0;     // This will be computed based on the input stream
  
    // |streaming| indicates whether or not we're currently streaming
    // video from the camera. Obviously, we start at false.
  
    var streaming = false;
  
    // The various HTML elements we need to configure or control. These
    // will be set by the startup() function.
  
    var video = null;
    var canvas = null;
    var photo = null;
    var startbutton = null;
    var formDataToUpload = [];
    var request;


    teacher = document.getElementById("id_teacher");
    lecture = document.getElementById("id_lecture");
    submit = document.getElementById("submit");

    function startup() {
      video = document.getElementById('video');
      canvas = document.getElementById('canvas');
      photo = document.getElementById('photo');
      filename = document.getElementById("filename");
      startbutton = document.getElementById('startbutton');
    
  
      navigator.mediaDevices.getUserMedia({video: true, audio: false})
      .then(function(stream) {
        video.srcObject = stream;
        video.play();
      })
      .catch(function(err) {
        console.log("An error occurred: " + err);
      });
  
      video.addEventListener('canplay', function(ev){
        if (!streaming) {
          height = video.videoHeight / (video.videoWidth/width);
        
          // Firefox currently has a bug where the height can't be read from
          // the video, so we will make assumptions if this happens.
        
          if (isNaN(height)) {
            height = width / (4/3);
          }
        
          video.setAttribute('width', width);
          video.setAttribute('height', height);
          canvas.setAttribute('width', width);
          canvas.setAttribute('height', height);
          streaming = true;
        }
      }, false);
  
      startbutton.addEventListener('click', function(ev){
        takepicture();
        ev.preventDefault();
      }, false);
      
      clearphoto();
    }
  
    // Fill the photo with an indication that none has been
    // captured.
  
    function clearphoto() {
      var context = canvas.getContext('2d');
      context.fillStyle = "#AAA";
      context.fillRect(0, 0, canvas.width, canvas.height);
  
      var data = canvas.toDataURL('image/png');

      photo.setAttribute('src', data);
    }
    
    // Capture a photo by fetching the current contents of the video
    // and drawing it into a canvas, then converting that to a PNG
    // format data URL. By drawing it on an offscreen canvas and then
    // drawing that to the screen, we can change its size and/or apply
    // other changes before drawing it.
  
    function takepicture() {
      var context = canvas.getContext('2d');
      if (width && height) {
        canvas.width = width;
        canvas.height = height;
        context.drawImage(video, 0, 0, width, height);
      
        var data = canvas.toDataURL('image/png');
        
        var form = document.getElementById("myAwesomeForm");

        var ImageURL = data; // 'photo' is your base64 image
        // Split the base64 string in data and contentType
        var block = ImageURL.split(";");
        // Get the content type of the image
        var contentType = block[0].split(":")[1];// In this case "image/gif"
        // get the real base64 content of the file
        var realData = block[1].split(",")[1];

        // Convert it to a blob to upload
        var blob = b64toBlob(realData, contentType);

        // Create a FormData and append the file with "image" as parameter name
        formDataToUpload = new FormData(form);
        formDataToUpload.append('image_file', blob);
        console.log(formDataToUpload.getAll(filename));
        photo.setAttribute('src', data);

      } else {
        clearphoto();
      }
    }



    function b64toBlob(b64Data, contentType, sliceSize) {
        contentType = contentType || '';
        sliceSize = sliceSize || 512;
    
        var byteCharacters = atob(b64Data); // window.atob(b64Data)
        var byteArrays = [];
    
        for (var offset = 0; offset < byteCharacters.length; offset += sliceSize) {
            var slice = byteCharacters.slice(offset, offset + sliceSize);
    
            var byteNumbers = new Array(slice.length);
            for (var i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }
    
            var byteArray = new Uint8Array(byteNumbers);
    
            byteArrays.push(byteArray);
        }
    
        var blob = new Blob(byteArrays, {type: contentType});
        return blob;
    }

    teacher.addEventListener('change', function(event){
      console.log("ohkkkkkkkkkkk")
      var teacher_value = teacher.value;
      formDataToUpload.append("teacher", teacher_value);
    });

    lecture.addEventListener('change', function(event){
      var lecture_value = lecture.value;
      formDataToUpload.append("lecture", lecture_value);
    });

    submit.addEventListener('click', function(event){
        
        request = new XMLHttpRequest();
        request.onreadystatechange = function() {
          if (this.readyState == 4 && this.status == 302) {
              var json = JSON.parse(this.responseText); 
              console.log(json.success);
              //following line would actually change the url of your window.  
              window.location.href = json.success; 
          }
        };
        request.open("POST", "");
        console.log(formDataToUpload)
        request.send(formDataToUpload);
        event.preventDefault();
    });

    
    // Set up our event listener to run the startup process
    // once loading is complete.  
    window.addEventListener('load', startup, false);
    
  })();