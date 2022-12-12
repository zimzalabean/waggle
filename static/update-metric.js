// JavaScript File to add event-handlers to "rate" a movie

// Ajax-style logins are done this way.


// a simple response handler you can use in raw debugging or demos

function showResponse(resp) {
    console.log('response is: ', resp);
}

// The response handler that the app uses in practice. It gets a response from the back end that looks like:

// {error: false, tt: 456, avg: 3.5}

// function processAverage(resp) {
//     console.log('response is ',resp);
//     // I didn't ask you to do this error reporting
//     if(resp.error) {
//         // inserting into an error section would 
//         // probably be better than an alert
//         alert('Error: '+resp.error);
//     }
//     var tt = resp.tt;
//     var avg = resp.avg;
//     console.log("New average for movie "+tt+" is "+avg);
//     $("[data-tt="+tt+"]").find(".avgrating").text(avg);
// }

/* global url_to_rate progressive_on uid */
/* The preceding globals are defined in the movie-list.html template */

// This code adds a delegated event handler to the #movies-list table that takes care of
// (1) making the chosen rating bold and
// (2) posting the Ajax request.
// It also adds the Ajax-login handler

// Have to wrap this in a document.ready because this file is loaded in the head.
$(function () { 


$("#movies-list").on('click',
                     '.movie-rating',
    function (event) {
        if(!progressive_on) return;

        if( event.target != this) return;
        $(this).closest("td").find("label").css("font-weight","normal");
        $(this).css("font-weight","bold");
        var tt = $(this).closest("[data-tt]").attr("data-tt");
        var stars = $(this).find("[name=stars]").val();
        // references the uid variable set by the template
        rateMovie(tt, stars);
    });
});

$(document).ready(function() {
    $('#form').on('submit',function(e){
        var comment_id = $('#comment_id').val()
        var kind = $('#kind').val();
        likeComment(comment_id, kind);
    });
  });

// ================================================================
// Above is all the browser event-handling work. Below are functions
// you can use for testing in the JavaScript console:

// core function to rate a movie via POST to base url and update the page

// function likePost(post_id, kind) {
//     console.log("user "+user_id+" "+ kind+ " "+post_id);
//     $.post(url_for_like_post, {'post_id': tt, 'kind': kind}, processAverage, 'json');
// }

function likeComment(comment_id, kind) {
    console.log("user "+ kind+ " "+comment_id);
    $.post("/likeComment/", {'comment_id': tt, 'kind': kind}, 'json');
}

// All these functions use the base_url + tt URL

// gets the current rating and updates the page

// function getPostLike(post_id) {
//     $.ajax(url_for_like_post+post_id, {method: 'GET',
//                                success: processAverage});
// }

function getCommentLike(comment_id) {
    $.ajax("/likeComment/"+comment_id, {method: 'GET'});
}
// uses the PUT method to replace the current rating and updates the page



// deletes the current user's rating and updates the page
