numberOfAccountsInput = document.getElementById('number-of-accounts');
fastCheckbox = document.getElementById('fast-checkbox');
generateUsernameForm = document.querySelector('.username-input-column');
usernameFormButton = document.getElementById('submit-username-form');

fillwithFilters = document.getElementById('filters');
fillWithHeader = document.querySelector('.fill-with-header');
fillWithResults = document.querySelector('.fill-with-results');

const differentLoading = ["dot-elastic", "dot-pulse", "dot-flashing", "dot-collision", "dot-revolution", "dot-carousel", "dot-typing", 
                          "dot-windmill", "dot-bricks", "dot-floating", "dot-fire", "dot-spin", "dot-falling", "dot-stretching"];
const yearNow = new Date().getFullYear();
let numberOfAccounts = 1;
let laststatus = '';

disableIfNoInput();

numberOfAccountsInput.addEventListener('change', function(event){
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

    usernameFormButton.disabled = true;
    disableIfNoInput();
});

usernameFormButton.addEventListener('click', async function(event){
    event.preventDefault();

    // Clears Everything
    document.getElementById('progress-container').innerHTML = '';
    fillwithFilters.innerHTML = '';
    fillwithFilters.classList.remove('filters');
    fillWithHeader.innerHTML = '';
    fillWithResults.innerHTML = '';
    numberOfAccounts = parseInt(numberOfAccountsInput.value);

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
    usernameFormButton.disabled = true;
    // Had to do this for cases where user submit with 'Enter'
    usernameFormButton.classList.add('disabled');
    numberOfAccountsInput.disabled = true;
    fastCheckbox.disabled = true;
}

function update_progress(status_url, progressList, usernames, deletedUsernames) {
    // Send GET request to status URL
    $.getJSON(status_url, function(data) {
        // Update progressList with progressListItems, back to pure Javascript
        if (laststatus != data['status']) {
            // Removes previous loading icon if not null
            const oldLoading = document.getElementById('loading');
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
            
            laststatus = data['status'];
            progressListItems.scrollIntoView({behavior: "smooth", block: "start", inline: "nearest"});
        }

        // If it is 'FAILURE' or 'DONE'
        if (data['state'] != 'PENDING' && data['state'] != 'PROGRESS') {
            const oldLoading = document.getElementById('loading');
            oldLoading.parentNode.removeChild(oldLoading);
            // > If not, the app has died, error has been printed
            if ('result' in data) {
                // Enables form
                numberOfAccountsInput.disabled = false;
                usernameFormButton.classList.remove('disabled');
                usernameFormButton.disabled = false;
                fastCheckbox.disabled = false;
                // Print result using function
                andTheResult = JSON.parse(data['result']);
                usernamesArray = removeInvalidUsernames(andTheResult, usernames, deletedUsernames);
                loadFilter();
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

function removeInvalidUsernames(data, usernames, deletedUsernames) {
    usernamesArray = [].slice.call(usernames);
    let numberOfAccountsDeleted = 0;
    for (let i = 0; i < numberOfAccounts + numberOfAccountsDeleted; i++) {
        if (deletedUsernames.includes(`${usernamesArray[i- numberOfAccountsDeleted].value}`)) {
            usernamesArray.splice(i - numberOfAccountsDeleted, 1);
            numberOfAccounts--;
            numberOfAccountsDeleted++;
        }
    }
    return usernamesArray;
}

function loadFilter() {
    fillwithFilters.classList.add('filters');
    fillwithFilters.innerHTML = `<div class="filter-container">
    <h5>Popularity</h5> <input type="text" class="popularity-js-range-slider" name="my_range" value="" />
    <div class="slide-texts"> <p class="slide-text">Well-known</p> <p class="slide-text">Obscure</p> </div> </div>
    <div class="filter-container"> <h5>Year</h5> <input type="text" class="year-js-range-slider" name="my_range" value="" />
    <div class="slide-texts"> <p class="slide-text">1920</p> <p class="slide-text">${yearNow}</p> </div>
    </div>`
    $(".popularity-js-range-slider").ionRangeSlider({
        type: "double",
        min: 0,
        max: 1000,
        from: 100,
        to: 1000,
        skin: "round",
        hide_from_to: true,
        onStart: function(data) {
            filterByPopularity(data.from, data.to);
        },
        onChange: function(data) {
            filterByPopularity(data.from, data.to);
        },
    });
    $(".year-js-range-slider").ionRangeSlider({
        type: "double",
        min: 1920,
        max: yearNow,
        from: 1940,
        to: yearNow,
        skin: "round",
        onStart: function(data) {
            filterByYear(data.from, data.to)
        },
        onChange: function(data) {
            filterByYear(data.from, data.to)
        },
    });
}

function addResults(data, usernames) {
    fillWithHeader.innerHTML = `<th scope="col"></th> 
                                <th scope="col">Letterboxd Rating</th>`;
    for (let i = 0; i < numberOfAccounts; i++){                           
        fillWithHeader.innerHTML += `<th scope="col">${usernames[i].value}'s<br> Predicted Rating</th>`;
    }
    if (numberOfAccounts != 1) {
        fillWithHeader.innerHTML += `<th scope="col">Average</th>`;
    }

    for (let i = 0; i < 1000; i++){
        const resultRow = document.createElement('tr');
        resultRow.classList.add('color-and-space');
        resultRow.setAttribute('data-vote-count', `${data.data[i].vote_count}`)
        let resultRowString = '';
        resultRowString += `<td class="responsive-bar"><div class="image-title-genre">
                                    <img class="movie-image" src="https://a.ltrbxd.com/resized/${data.data[i].image_url}.jpg"/>
                                    <div class="title-genre">
                                        <p class="title">${data.data[i].movie_title} (${data.data[i].year_released})</p>
                                        <ul class='genre-items'>`;
        if (data.data[i].genres != null) {
            console.log(data.data[i].genres);
            for (genre of data.data[i].genres){
                console.log(genre);
                resultRowString += `     <li class="genre-item">${genre[0].toUpperCase() + genre.slice(1)}</li>`;
            }
        }
        
        resultRowString += `</ul></div></div></td>
                            <td><span class="add-info">${(data.data[i].vote_average / 10).toFixed(2)}</span></td>`;
        for (let j = 0; j < numberOfAccounts; j++){
            resultRowString += `<td><span class="add-info">${(data.data[i][`score_${j}`] / 10).toFixed(2)}</span></td>`;
        }
        if (numberOfAccounts != 1) {
            resultRowString += `<td><span class="add-info">${(data.data[i]['mean_score'] / 10).toFixed(2)}</span></td>`;
        }
        resultRow.innerHTML = resultRowString;
        fillWithResults.appendChild(resultRow);
    }
    fillwithFilters.scrollIntoView({behavior: "smooth", block: "start", inline: "nearest"});
}


// Disables submit button if no input
function disableIfNoInput() {
    $("form input").on("keyup change",function () {
        var empty = false;
        $("form input").each(function() {
            if ($(this).val() == '') {
                empty = true;
            }
        });
        if (empty) {
            $('input[type="submit"]').attr('disabled', 'disabled');
        } else {
            $('input[type="submit"]').removeAttr('disabled');
        }
    });
}

// Slider
function filterByPopularity(startPopularity, endPopularity) {
    // From a scale of 0 to 1000, 0 is most popular
    tableRows = document.querySelectorAll('.color-and-space');
    tableRows.forEach((tableRow) => {
        numberWatched = tableRow.getAttribute("data-vote-count");
        // Sort of split into 2 tiers. Tier 1: >1m, Tier 2: <1m
        if (numberWatched > 1000000) numberWatchedPercentile = 100 - ((numberWatched - 1000000) / 1000000) * 100;
        else numberWatchedPercentile = 1000 - (numberWatched / 1000000) * 900;
        if (numberWatchedPercentile < startPopularity || numberWatchedPercentile > endPopularity) {
            // tableRow.style.display = "none";
            tableRow.classList.add('collapse')
        }
        else tableRow.classList.remove('collapse')
    });
}

function filterByYear(startYear, endYear) {
    tableRows = document.querySelectorAll('.color-and-space');
    tableRows.forEach((tableRow) => {
        year = tableRow.childNodes[0].innerHTML.split('</p>')[0].substr(-5).slice(0, -1);
        if (startYear > year || endYear < year) {
            tableRow.classList.add('collapse')
        }
        else tableRow.classList.remove('collapse')
    });
}