var timer;
$(document).ready(function() {
    timer = setInterval('refreshLog()', 5000); // refresh the log and card counts every 5 seconds
});

function refreshLog() {
    game_code = window.location.pathname.split('/')[1];
    $.ajax({
        url:'/'+game_code+'/log',
        type:"GET",
        success: function(result) {
            if (result != "" && result != $('#log').html()) {
                $("#log").html(result);
                $("#log").scrollTop($("#log").scrollHeight)
            }
        },
        error: function(error) {
            console.log("Stopping auto refresh because of error");
            clearInterval(timer);
        }

    })
    $.ajax({
        url:'/'+game_code+'/card_nums',
        type:"GET",
        success: function(result) {
            $("#pcount").text(result.cardNums[0])
            $("#gcount").text(result.cardNums[1])
            $("#scount").text(result.cardNums[2])
            $("#lcount").text(result.cardNums[3])
            $("#hcount").text(result.cardNums[4])
            $("#gascount").text(result.cardNums[5])
            $("#crisis-count").text(result.cardNums[6])
        },
        error: function(error) {
            console.log("Stopping auto refresh because of error");
            clearInterval(timer);
        }

    })
}

$( "#undo-previous" ).submit(async function( event ) {
    event.preventDefault();
    game_code = window.location.pathname.split('/')[1];
    player_name = window.location.pathname.split('/')[2];
    $.ajax({
        url: '/' + game_code + '/' + player_name + '/undo_action',
        type: 'PUT',
        success: function(result) {
            console.log(result);
            if (result == "Revert did nothing") {
                console.log("did nothing");
                $("#success-nomore-undo").removeAttr("hidden");
                $("#error-undo").attr("hidden", true)
                $("#success-undo").attr("hidden", true)
                setTimeout(() => { $("#success-nomore-undo").attr("hidden", true)}, 3000);
            }
            else {
                console.log("successfully reverted");
                $("#success-undo").removeAttr("hidden");
                $("#error-undo").attr("hidden", true)
                $("#success-nomore-undo").attr("hidden", true)
                setTimeout(() => { $("#success-undo").attr("hidden", true)}, 3000);
            }
        },
        error: function(error) {
            console.log(error);
            $("#error-undo").removeAttr("hidden");
            $("#success-undo").attr("hidden", true)
            $("#success-nomore-undo").attr("hidden", true)
            setTimeout(() => { $("#error-undo").attr("hidden", true)}, 3000);
        }
    })
})

// submit search request to server
$( "#search-form" ).submit(async function( event ) {
    // stop the normal function of submit
    event.preventDefault();
    game_code = window.location.pathname.split('/')[1];
    player_name = window.location.pathname.split('/')[2];
    deckType = $("#location").val();
    cardNum = $("#lookNum").val()
    $.ajax({
        url:'/' + game_code + '/' + player_name + '/card_decks',
        type:"GET",
        data: {deckType: deckType, cardNum: cardNum},
        success: function(result) {
            console.log(result)
            for(var i = 1; i <= 6; i++) {
                id = "#card" + (i).toString();
                $(id).attr("hidden", true);
            }
            for(var i = 0; i < result.cards.length; i++) {
                id = "#card" + (i+1).toString();
                $(id).removeAttr("hidden");
                $(id).html($(id).html().split('>')[0] + "> " + result.cards[i]);
                $(id+"-check").val(result.cards[i].split('> ')[1]);
            }
            $("#card-display").removeAttr("hidden");
            $("#take-form").removeAttr("hidden");
        },
        error: function(error) {
            console.log(error);
        }
    })
});

// submit take cards request to server
$( "#take-form" ).submit(async function( event ) {
    // stop the normal function of submit
    event.preventDefault();
    game_code = window.location.pathname.split('/')[1];
    player_name = window.location.pathname.split('/')[2];
    deckType = $("#location").val();
    cardList = "";
    fullList = "";
    
    if($("#card1-check").val() != "on") {
        if($("#card1-check").is(":checked")) 
            cardList += ", " + $("#card1-check").val()
        fullList += ", " + $("#card1-check").val()
    }
    if($("#card2-check").val() != "on") {
        if($("#card2-check").is(":checked")) 
            cardList += ", " + $("#card2-check").val()
        fullList += ", " + $("#card2-check").val()
    }
    if($("#card3-check").val() != "on") {
        if($("#card3-check").is(":checked")) 
            cardList += ", " + $("#card3-check").val()
        fullList += ", " + $("#card3-check").val()
    }
    if($("#card4-check").val() != "on") {
        if($("#card4-check").is(":checked")) 
            cardList += ", " + $("#card4-check").val()
        fullList += ", " + $("#card4-check").val()
    }
    if($("#card5-check").val() != "on") {
        if($("#card5-check").is(":checked")) 
            cardList += ", " + $("#card5-check").val()
        fullList += ", " + $("#card5-check").val()
    }
    if($("#card6-check").val() != "on") {
        if($("#card6-check").is(":checked")) 
            cardList += ", " + $("#card6-check").val()
        fullList += ", " + $("#card6-check").val()
    }
    if (cardList.length > 2)
        cardList = cardList.substr(2);
    if (fullList.length > 2)
        fullList = fullList.substr(2);

    console.log(deckType)
    console.log(cardList)
    console.log(fullList)
    $.ajax({
        url:'/' + game_code + '/' + player_name + '/card_decks',
        type:"DELETE",
        data: {deckType: deckType, cardList: cardList, fullList: fullList},
        success: function(result) {
            console.log(result)
            $("#card-display").attr("hidden", true);
            $("#take-form").attr("hidden", true);
            // set the check vals back to 'on'
            $("#card1-check").val("on");
            $("#card2-check").val("on");
            $("#card3-check").val("on");
            $("#card4-check").val("on");
            $("#card5-check").val("on");
            $("#card6-check").val("on");
        },
        error: function(error) {
            console.log(error);
        }
    })
});

$( "#crisis-form" ).submit(async function( event ) {
    event.preventDefault();
    game_code = window.location.pathname.split('/')[1];
    player_name = window.location.pathname.split('/')[2];
    card = $("#crisis-card").val();
    loc = $("#crisis-card-loc").val();

    $.ajax({
        url:'/' + game_code + '/' + player_name + '/crisis_deck',
        type:"PUT",
        data:{card: card, loc: loc},
        success: function(result) {
            console.log(result);
            $("#crisis-card").val('');
            $("#crisis-card-loc").val('');
            $("#submit-crisis-success").removeAttr("hidden");
            $("#submit-crisis-error").attr("hidden", true);
        },
        error: function(error) {
            console.log(error);
            $("#submit-crisis-success").attr("hidden", true);
            $("#submit-crisis-error").removeAttr("hidden");
        }
    })
});
$( "#reveal-crisis-form" ).submit(async function( event ) {
    event.preventDefault();
    game_code = window.location.pathname.split('/')[1];
    player_name = window.location.pathname.split('/')[2];

    $.ajax({
        url:'/' + game_code + '/' + player_name + '/crisis_deck',
        type:"GET",
        success: function(result) {
            console.log(result);
            $("#crisis-reveal").html(result);
            $("#crisis-cards-div").removeAttr("hidden");
        },
        error: function(error) {
            console.log(error);
            $("#crisis-cards-div").attr("hidden", true);
        }
    })
});
$( "#clear-crisis-form" ).submit(async function( event ) {
    event.preventDefault();
    game_code = window.location.pathname.split('/')[1];
    player_name = window.location.pathname.split('/')[2];

    $.ajax({
        url:'/' + game_code + '/' + player_name + '/crisis_deck',
        type:"DELETE",
        success: function(result) {
            console.log(result);
            $("#crisis-reveal").html(result);
            $("#crisis-cards-div").attr("hidden", true);
        },
        error: function(error) {
            console.log(error);
        }
    })
});