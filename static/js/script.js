numberOfAccountsInput = document.getElementById('number-of-accounts');
generateUsernameForm = document.querySelector('.username-input-column');
usernameFormButton = document.getElementById('submit-username-form');

fillWithHeader = document.querySelector('.fill-with-header');
fillWithResults = document.querySelector('.fill-with-results');

let numberOfAccounts = 1;
let laststatus = '';

numberOfAccountsInput.addEventListener('change', function(event){
    numberOfAccounts = parseInt(event.target.value);
    generateUsernameForm.innerHTML = "";
    for (let i = 1; i <= numberOfAccounts; i++){
        const form = document.createElement('input');
        form.setAttribute('type', 'text');
        form.setAttribute('class', 'username-input');
        form.setAttribute('name', `username_${i}`);
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
            update_progress(status_url, progressList[0], usernames);
        },
        error: function() {
            alert('Unexpected error. Try again later? :(');
        }
    });
}

function update_progress(status_url, progressList, usernames) {
    // Send GET request to status URL

    $.getJSON(status_url, function(data) {
        // Update progressList with progressListItems, back to pure Javascript
        if (laststatus != data['status']) {
            const progressListItems = document.createElement('li');
            progressListItems.innerText = data['status'];
            progressList.appendChild(progressListItems);
            laststatus = data['status']
            progressListItems.scrollIntoView({behavior: "smooth", block: "start", inline: "nearest"});
        }

        // If it is 'FAILURE' or 'DONE'
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            if ('result' in data) {
                // Print result using function
                andTheResult = JSON.parse(data['result'])
                addResults(andTheResult, usernames);
            }
            else {
                // Everything finished but no results, print out the error stored in 'state'
                $(progressList).text('Result: ' + data['state']);
            }
        }
        else {
            // Run again after 5 seconds
            setTimeout(function() {
                update_progress(status_url, progressList, usernames);
            }, 5000);
        }
    });
}

function addResults(data, usernames) {
    console.log(usernames)
    console.log(usernames[0])
    console.log(usernames[0].value)
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

        for (let j = 1; j <= numberOfAccounts; j++){                           
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
}