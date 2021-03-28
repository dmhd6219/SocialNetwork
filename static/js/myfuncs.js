function AddFriend(user1_id, user2_id) {
    var http = new XMLHttpRequest();
    var url = `/api/friends/${user1_id}/${user2_id}`;
    var params = ``;
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

function DeleteFriend(user1_id, user2_id) {
    var http = new XMLHttpRequest();
    var url = `/api/friends/${user1_id}/${user2_id}`;
    var params = ``;
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


function CreatePost(user_id) {
    var http = new XMLHttpRequest();
    var url = `/api/posts/${user_id}`;
    var params = `text=${document.getElementById('createpost').value}`;
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