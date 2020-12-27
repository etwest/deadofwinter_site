// submit join-game request to server
$( "#players-form" ).submit(async function( event ) {
    // stop the normal function of submit
    event.preventDefault();
    player_name = $('input[name="name"]:checked').val();
    game_code = window.location.pathname.split('/')[1];
    console.log(game_code)
    $.ajax({
        url:'/' + game_code + '/init_player',
        type:"GET",
        data:{player_name: player_name},
        success: function(result) {
            console.log(result)
            $("#objective").html("Secret Objective: <b>"+result.objective+
                "</b><br>Starting Cards: " + result.cards
                + "<br>Shuffle the decks and take the matching cards. This is the only time this info will be shown.");
            $("#objective_display").removeAttr("hidden");
            $("#error").attr("hidden", true);
            $("#enter-player").attr("hidden", true);
            $("#begin-game").attr("onclick", "location.href='/" + game_code + '/' + player_name + "/game';")
        },
        error: function(error) {
            console.log(error);
            $("#error").text(error.responseText)
            $("#error").removeAttr("hidden");
            $("#objective_display").attr("hidden", true);
        }
    })
});