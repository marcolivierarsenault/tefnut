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

});

function get_state(){
    $.post( "state", function( data ) {
        var obj = jQuery.parseJSON(data );
        $( ".result" ).json( data );
      });
}
