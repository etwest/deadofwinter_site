// submit new-game request to server
$( "#new-game-form" ).submit(async function( event ) {
    // stop the normal function of submit
    event.preventDefault();

    // send to the server
    players_text = $("#player-list").val();
    betray_variant = "standard"
    if ($("#no_betray").is(":checked")) {
        betray_variant = "none"
    }
    if ($("#big_betray").is(":checked")) {
        betray_variant = "betrayer"
    }
    $.ajax({
        url:"/init",
        type:"POST",
        data:{player_list: players_text, betray:betray_variant},
        success: function(result) {
            console.log(result)
            $("#success").text("Successfully created new game! Game Code: " + result.gameCode)
            $("#success").removeAttr("hidden");
            $("#error").attr("hidden", true);
        },
        error: function(error) {
            console.log(error);
            $("#error").removeAttr("hidden");
            $("#success").attr("hidden", true);
        }
    })
});

// submit join-game request to server
$( "#join-game" ).submit(async function( event ) {
    // stop the normal function of submit
    event.preventDefault();

    // send to the server
    game_code = $("#game-code").val();
    window.location.href = '/' + game_code + '/join'
});