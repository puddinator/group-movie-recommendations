numberOfAccounts = document.getElementById('number-of-accounts');
usernameForm = document.querySelector('.username-input-column');

function addFormInputBoxes(numberOfAccounts) {

}

numberOfAccounts.addEventListener('change', function(event){
    usernameForm.innerHTML = "";
    for (let i = 1; i <= event.target.value; i++){
        const form = document.createElement('input');
        form.setAttribute('type', 'text');
        form.setAttribute('class', 'username-input');
        form.setAttribute('name', 'site-username');
        form.setAttribute('placeholder', 'Letterboxd Username');
        usernameForm.appendChild(form);
    }
});