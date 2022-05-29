numberOfAccountsInput = document.getElementById('number-of-accounts');
generateUsernameForm = document.querySelector('.username-input-column');
usernameFormButton = document.getElementById('submit-username-form');

fillWithHeader = document.querySelector('.fill-with-header');
fillWithResults = document.querySelector('.fill-with-results');

numberOfAccounts = 1;

numberOfAccountsInput.addEventListener('change', function(event){
    numberOfAccounts = event.target.value;
    generateUsernameForm.innerHTML = "";
    for (let i = 1; i <= numberOfAccounts; i++){
        const form = document.createElement('input');
        form.setAttribute('type', 'text');
        form.setAttribute('class', 'username-input');
        form.setAttribute('id', `site_username_${i}`);
        form.setAttribute('placeholder', 'Letterboxd Username');
        generateUsernameForm.appendChild(form);
    }
});

usernameFormButton.addEventListener('click', async function(event){
    event.preventDefault();

    const username1 = document.getElementById("site_username_1").value;
    const response = await fetch(`/results?number_of_accounts=${numberOfAccounts}&username_1=${username1}`, {
        method: 'GET'
    });
    
    const data = await response.json();
    console.log(data);
    addResults(data);
});

function addResults(data) {
    fillWithHeader.innerHTML = `<th style="width:10%" scope="col">#</th> <th style="width:70%" scope="col">Movie</th> <th style="width:20%" scope="col">Score</th>`;

    for (let i = 1; i <= 50; i++){
        const resultRow = document.createElement('tr');
        const resultRowNo = document.createElement('th');
        resultRowNo.setAttribute('scope', 'row');
        resultRowNo.innerText = i;
        resultRow.appendChild(resultRowNo);
        const resultRowMovie = document.createElement('td');
        resultRowMovie.innerText = data.data[i - 1].movie_id;
        resultRow.appendChild(resultRowMovie);
        const resultRowScore = document.createElement('td');
        resultRowScore.innerText = data.data[i - 1]['score'];
        resultRow.appendChild(resultRowScore);
        fillWithResults.appendChild(resultRow);
    }
}