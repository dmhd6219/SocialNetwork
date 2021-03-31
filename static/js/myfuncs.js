function AddFriend(user1_id, user2_id) {
    var http = new XMLHttpRequest();
    var url = `/api/friends/${user1_id}/${user2_id}`;
    var params = ``;
    http.open('POST', url, true);

    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    http.send(params);

    let friends = document.getElementById('friends-count');
    friends.innerHTML = String(Number(friends.innerHTML) + 1)

    let button = document.getElementById('friends-button');
    button.innerHTML = 'Delete friend';
    button.setAttribute('class', 'btn btn-outline-danger rounded-pill mb-3');
    button.setAttribute('onclick', `DeleteFriend(${user1_id}, ${user2_id})`);
}

function DeleteFriend(user1_id, user2_id) {
    var http = new XMLHttpRequest();
    var url = `/api/friends/${user1_id}/${user2_id}`;
    var params = ``;
    http.open('DELETE', url, true);

    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    http.send(params);

    let friends = document.getElementById('friends-count');
    friends.innerHTML = String(Number(friends.innerHTML) - 1);

    let button = document.getElementById('friends-button');
    button.innerHTML = 'Add as friend';
    button.setAttribute('class', 'btn btn-outline-primary rounded-pill mb-3');
    button.setAttribute('onclick', `AddFriend(${user1_id}, ${user2_id})`);
}


function CreatePost(user_id) {
    var http = new XMLHttpRequest();
    var url = `/api/posts/${user_id}`;
    let post_text = document.getElementById('createpost').value;
    var params = `text=${post_text}`;
    http.open('POST', url, true);

    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function () {//Call a function when the state changes.
        if (http.readyState == 4 && http.status == 200) {
            alert(http.responseText);
            location.reload();
        }
    }
    http.send(params);
}

function DeletePost(post_id) {
    var http = new XMLHttpRequest();
    var url = `/api/post/${post_id}`;
    var params = `text=${document.getElementById('createpost').value}`;
    http.open('DELETE', url, true);

    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function () {//Call a function when the state changes.
        if (http.readyState == 4 && http.status == 200) {
            alert(http.responseText);
            location.reload();
        }
    }
    http.send(params);
}

function StartPlayback(token, uri) {
    fetch(`https://api.spotify.com/v1/me/player/play`, {
            method: 'PUT',
            body: JSON.stringify({uris: [uri]}),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        }
    )
}


function MouseOverTrack(index) {
    let track = document.getElementById(`track-line${index}`);
    track.style.color = 'rgb(80,181,255)'

    let track_index = document.getElementById(`track-index${index}`);
    track_index.innerHTML = `<i class='ri-play-circle-line' style='pointer-events: none'>`

}

function MouseOutTrack(index) {
    let track = document.getElementById(`track-line${index}`);
    track.style.color = ''

    let track_index = document.getElementById(`track-index${index}`);
    track_index.innerHTML = index
}

function FollowArtist(token, id) {
    fetch(`https://api.spotify.com/v1/me/following?type=artist&ids=` + id, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                "Accept": "application/json"
            },
        }
    )

    let follow_button = document.getElementById('follow-button')
    follow_button.innerHTML = 'Unfollow'
    follow_button.onclick = "UnfollowArtist(`{{spotify.auth_manager.get_access_token()['access_token']}}`, `{{artist['id']}}`)"

}

function UnfollowArtist(token, id) {
    fetch(`https://api.spotify.com/v1/me/following?type=artist&ids=` + id, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                "Accept": "application/json"
            },
        }
    )

    let follow_button = document.getElementById('follow-button')
    follow_button.innerHTML = 'Follow'
    follow_button.onclick = "FollowArtist(`{{spotify.auth_manager.get_access_token()['access_token']}}`, `{{artist['id']}}`)"
}
