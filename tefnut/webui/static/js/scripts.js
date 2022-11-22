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

    $('#btn_auto').click(function() {
        if (current_mode != "AUTO"){
            $('#modal_mode').text("AUTO");
            $('.modal').addClass("is-active");
            
            $('#modal_accept').click(function() {
                $('.modal').removeClass("is-active");
                $('#modal_accept').off('click');
                $('#modal_cancel').off('click');
                reset_ui();
                get_state(JSON.stringify({"mode": "AUTO"}))
            });

            $('#modal_cancel').click(function() {
                $('.modal').removeClass("is-active");
                $('#modal_accept').off('click');
                $('#modal_cancel').off('click');
            });
        }
    });

    $('#btn_manual').click(function() {
        if (current_mode != "MANUAL"){
            $('#modal_mode').text("MANUAL");
            $('.modal').addClass("is-active");
            
            $('#modal_accept').click(function() {
                $('.modal').removeClass("is-active");
                $('#modal_accept').off('click');
                $('#modal_cancel').off('click');
                reset_ui();
                get_state(JSON.stringify({"mode": "MANUAL"}))
            });

            $('#modal_cancel').click(function() {
                $('.modal').removeClass("is-active");
                $('#modal_accept').off('click');
                $('#modal_cancel').off('click');
            });
        }
    });

    $('#btn_off').click(function() {
        if (current_mode != "OFF"){
            $('#modal_mode').text("OFF");
            $('.modal').addClass("is-active");
            
            $('#modal_accept').click(function() {
                $('.modal').removeClass("is-active");
                $('#modal_accept').off('click');
                $('#modal_cancel').off('click');
                reset_ui();
                get_state(JSON.stringify({"mode": "OFF"}))
            });

            $('#modal_cancel').click(function() {
                $('.modal').removeClass("is-active");
                $('#modal_accept').off('click');
                $('#modal_cancel').off('click');
            });
        }
    });

    $('#btn_target').click(function() {
        value = Number($('#target_input').val())
        if (isNaN(value)) {
            alert("WORNG")
            return 1
        } else {
            alert("GOOD")

        }
    });

    setTimeout(get_state, 400);

});

var current_mode = ""

function get_state(data_to_send=NaN){
    $.post( "state", data_to_send, function( data, status ) {
        if (status == "success") {
            current_mode = data.mode
            $('#mode').html(data.mode);
            $('#state').html(data.state);
            $('#humidity').html(data.humidity + " %");
            $('#setpoint').html(data.target_humidity + " %");
            switch(data.mode) {
                case "AUTO":
                    $('#btn_auto').addClass("is-success");
                    $('#btn_auto').prop('disabled', false);
                    $('#btn_manual').prop('disabled', false);
                    $('#btn_off').prop('disabled', false);
                  break;
                case "MANUAL":
                    $('#btn_manual').addClass("is-info");
                    $('#btn_manual').prop('disabled', false);
                    $('#btn_auto').prop('disabled', false);
                    $('#btn_off').prop('disabled', false);
                    $('#target_input').prop('disabled', false);
                    $('#btn_target').prop('disabled', false);
                  break;
                default:
                    $('#btn_off').addClass("is-danger");
                    $('#btn_off').prop('disabled', false);
                    $('#btn_auto').prop('disabled', false);
                    $('#btn_manual').prop('disabled', false);
              }
        }
      }, "json");
};

function reset_ui(){
    $('#mode').html('<span class="icon"> <i class="fas fa-spinner"></i></span>');
    $('#state').html('<span class="icon"> <i class="fas fa-spinner"></i></span>');
    $('#humidity').html('<span class="icon"> <i class="fas fa-spinner"></i></span>');
    $('#setpoint').html('<span class="icon"> <i class="fas fa-spinner"></i></span>');
    $('#btn_auto').removeClass("is-success");
    $('#btn_manual').removeClass("is-info");
    $('#btn_off').removeClass("is-danger");
    $('#btn_auto').prop('disabled', true);
    $('#btn_manual').prop('disabled', true);
    $('#btn_off').prop('disabled', true);
    $('#target_input').prop('disabled', true);
    $('#btn_target').prop('disabled', true);
};
