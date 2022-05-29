numberOfAccountsInput = document.getElementById('number-of-accounts');
generateUsernameForm = document.querySelector('.username-input-column');
usernameFormButton = document.getElementById('submit-username-form');

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
    console.log(username1);
    const response = await fetch(`/results?number_of_accounts=${numberOfAccounts}&username_1=${username1}`, {
        method: 'GET'
    });
    
    const data = await response.json();
    console.log(response);
    console.log(data);
});