$(document).ready(function() {

    // Check for click events on the navbar burger icon
    $(".navbar-burger").click(function() {
  
        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");
  
    });

        // Check for click events on the navbar burger icon
    $(".navbar-menu").click(function() {
  
        // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
        $(".navbar-burger").toggleClass("is-active");
        $(".navbar-menu").toggleClass("is-active");
  
    });

    $(".testboutton").click(function() {
  
        print("ALLOs")
  
    });

    setTimeout(get_state, 3000);

});

function get_state(data_to_send){
    $.post( "state", data_to_send, function( data, status ) {
        if (status == "success") {
            $('#mode').html(data.mode);
            $('#state').html(data.state);
            $('#humidity').html(data.humidity);
            $('#setpoint').html(data.target_humidity);
            switch(data.mode) {
                case "AUTO":
                    $('#btn_auto').addClass("is-success");
                  break;
                case "MANUAL":
                    $('#btn_manual').addClass("is-info");
                    $('#target_input').prop('disabled', false);
                    $('#btn_target').prop('disabled', false);
                  break;
                default:
                $('#btn_off').addClass("is-danger");
              }
        }
      });
};

function reset_ui(){
    $('#mode').html('<span class="icon"> <i class="fas fa-spinner"></i></span>');
    $('#state').html('<span class="icon"> <i class="fas fa-spinner"></i></span>');
    $('#humidity').html('<span class="icon"> <i class="fas fa-spinner"></i></span>');
    $('#setpoint').html('<span class="icon"> <i class="fas fa-spinner"></i></span>');
    $('#btn_auto').removeClass("is-success");
    $('#btn_manual').removeClass("is-info");
    $('#btn_off').removeClass("is-danger");
    $('#target_input').prop('disabled', true);
    $('#btn_target').prop('disabled', true);
};
