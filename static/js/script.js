numberOfAccountsInput = document.getElementById('number-of-accounts');
generateUsernameForm = document.querySelector('.username-input-column');
usernameFormButton = document.getElementById('submit-username-form');

fillWithHeader = document.querySelector('.fill-with-header');
fillWithResults = document.querySelector('.fill-with-results');

const differentLoading = ["dot-elastic", "dot-pulse", "dot-flashing", "dot-collision", "dot-revolution", "dot-carousel", "dot-typing", 
                          "dot-windmill", "dot-bricks", "dot-floating", "dot-fire", "dot-spin", "dot-falling", "dot-stretching"];
let numberOfAccounts = 1;
let laststatus = '';

disableIfNoInput();

numberOfAccountsInput.addEventListener('change', function(event){
    usernameFormButton.disabled = true;
    disableIfNoInput();
    numberOfAccounts = parseInt(event.target.value);
    generateUsernameForm.innerHTML = "";
    for (let i = 1; i <= numberOfAccounts; i++){
        const form = document.createElement('input');
        form.setAttribute('type', 'text');
        form.setAttribute('class', 'username-input');
        form.setAttribute('id', 'username');
        form.setAttribute('name', `username_${i}`);
        form.setAttribute('autocomplete', 'on');
        form.setAttribute('placeholder', 'Letterboxd Username');
        generateUsernameForm.appendChild(form);        
    }
});

usernameFormButton.addEventListener('click', async function(event){
    event.preventDefault();

    let usernameForm = document.getElementById("username-form");
    let fd = new FormData(usernameForm);
    start_long_task(fd);
});

function start_long_task(fd) {
    const usernames = document.querySelectorAll(".username-input");
    deletedUsernames = [];

    progressList = $('<ul id="progress-list"></ul>');
    $('#progress-container').append(progressList);    

    $.ajax({
        type: 'POST',
        url: `/results`,
        data: fd,
        processData: false,
        contentType: false,
        success: function(data, status, request) {
            status_url = request.getResponseHeader('Location');
            update_progress(status_url, progressList[0], usernames, deletedUsernames);
        },
        error: function() {
            alert('Unexpected error sending your information. Try again later? :(');
        }
    });
    // Disables form
    numberOfAccountsInput.disabled = true;
    usernameFormButton.disabled = true;
}

function update_progress(status_url, progressList, usernames, deletedUsernames) {
    // Send GET request to status URL

    $.getJSON(status_url, function(data) {
        // Update progressList with progressListItems, back to pure Javascript
        if (laststatus != data['status']) {
            // Removes previous loading icon if not null
            const oldLoading = document.getElementById('loading')
            if (oldLoading != null) {
                oldLoading.parentNode.removeChild(oldLoading);
            }
            
            // Updates with new status
            const progressListItems = document.createElement('li');
            progressListItems.innerText = data['status'];
            progressList.appendChild(progressListItems);

            // Take note of removed usernames
            if (data['status'].slice(0, 4) == 'User'){
                deletedUsernames.push(`${data['status'].slice(14).slice(0, -60)}`);
            }
            
            // Adds in random loading icon below
            random = Math.floor(Math.random() * 14);
            const loading = document.createElement('span');
            loading.setAttribute('class', `${differentLoading[random]}`);
            loading.setAttribute('id', 'loading');
            progressList.appendChild(loading);
            
            laststatus = data['status']
            progressListItems.scrollIntoView({behavior: "smooth", block: "start", inline: "nearest"});
        }

        // If it is 'FAILURE' or 'DONE'
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            const oldLoading = document.getElementById('loading')
            oldLoading.parentNode.removeChild(oldLoading);
            
            if ('result' in data) {
                // If not, the app has died, error has been printed
                // Print result using function
                andTheResult = JSON.parse(data['result'])
                usernamesArray = removeInvalidUsernames(andTheResult, usernames, deletedUsernames);
                addResults(andTheResult, usernamesArray);
            }
        }
        else {
            // Run again after 5 seconds
            setTimeout(function() {
                update_progress(status_url, progressList, usernames, deletedUsernames);
            }, 5000);
        }
    });
}

function removeInvalidUsernames(data, usernames, deletedUsernames){
    usernamesArray = [].slice.call(usernames);
    let numberOfAccountsDeleted = 0;
    for (let i = 0; i < numberOfAccounts + numberOfAccountsDeleted; i++) {
        if (deletedUsernames.includes(`${usernamesArray[i- numberOfAccountsDeleted].value}`)) {
            usernamesArray.splice(i - numberOfAccountsDeleted, 1)
            numberOfAccounts--;
            numberOfAccountsDeleted++;
        }
    }
    return usernamesArray;
}

function addResults(data, usernames) {
    // genres image_url movie_id movie_title year_released vote_average vote_count 
    fillWithHeader.innerHTML = `<th scope="col">#</th> 
                                <th scope="col">Poster</th> 
                                <th scope="col">Movie</th> 
                                <th scope="col">Year</th> 
                                <th scope="col">Genre</th>
                                <th scope="col">Letterboxd No of Votes</th> 
                                <th scope="col">Letterboxd Score</th>`;
    for (let i = 0; i < numberOfAccounts; i++){                           
        fillWithHeader.innerHTML += `<th scope="col">${usernames[i].value}'s Score</th>`;
    }
    fillWithHeader.innerHTML += `<th scope="col">Average Score</th>`;

    for (let i = 1; i <= 100; i++){
        const resultRow = document.createElement('tr');

        const resultRowNo = document.createElement('th');
        resultRowNo.setAttribute('scope', 'row');
        resultRowNo.innerText = i;
        resultRow.appendChild(resultRowNo);

        const resultRowPoster = document.createElement('td');
        resultRowPoster.innerHTML = `<img class="my-github-image" src="https://a.ltrbxd.com/resized/${data.data[i - 1].image_url}.jpg">`;
        resultRow.appendChild(resultRowPoster);

        const resultRowMovie = document.createElement('td');
        resultRowMovie.innerText = data.data[i - 1].movie_title;
        resultRow.appendChild(resultRowMovie);

        const resultRowYear = document.createElement('th');
        resultRowYear.innerText = data.data[i - 1].year_released;
        resultRow.appendChild(resultRowYear);

        const resultRowGenre = document.createElement('td');
        resultRowGenre.innerText = data.data[i - 1].genres;
        resultRow.appendChild(resultRowGenre);

        const resultRowVotes = document.createElement('td');
        resultRowVotes.innerText = data.data[i - 1].vote_count;
        resultRow.appendChild(resultRowVotes);

        const resultRowAverageScore = document.createElement('td');
        resultRowAverageScore.innerText = data.data[i - 1].vote_average;
        resultRow.appendChild(resultRowAverageScore);

        for (let j = 0; j < numberOfAccounts; j++){                           
            const resultRowUserScore = document.createElement('td');
            resultRowUserScore.innerText = data.data[i - 1][`score_${j}`].toFixed(1);
            resultRow.appendChild(resultRowUserScore);
        }

        const resultRowMeanScore = document.createElement('td');
        resultRowMeanScore.innerText = data.data[i - 1]['mean_score'].toFixed(1);
        resultRow.appendChild(resultRowMeanScore);

        fillWithResults.appendChild(resultRow);
    }
    fillWithHeader.scrollIntoView({behavior: "smooth", block: "start", inline: "nearest"});
    // Enables form
    numberOfAccountsInput.disabled = false;
    usernameFormButton.disabled = false;
}


// Disables submit button if no input
function disableIfNoInput() {
    $("form input").keyup(function() {
        var empty = false;
        $("form input").each(function() {
            if ($(this).val() == '') {
                empty = true;
            }
        });
        if (empty) {
            $('input[type="submit"]').attr('disabled', 'disabled'); // updated according to http://stackoverflow.com/questions/7637790/how-to-remove-disabled-attribute-with-jquery-ie
        } else {
            $('input[type="submit"]').removeAttr('disabled'); // updated according to http://stackoverflow.com/questions/7637790/how-to-remove-disabled-attribute-with-jquery-ie
        }
    });
}