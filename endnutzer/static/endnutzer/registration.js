$(document).ready(() => {
    console.log('LOADING')
    $('#btnSubmit').click((event)=>{
        const pw = document.getElementById('id_password').value;
        const pw_comparison = document.getElementById('id_password_comparison').value;

        const comparison = pw === pw_comparison;

        const alertDiv = document.getElementById('pw-alert');

        if (!comparison) {
            event.preventDefault();
            alertDiv.classList = 'alert alert-danger';
            alertDiv.innerText = 'Die beiden Passwörter stimmen nicht überein!';
            return false;
        } else {
            alertDiv.classList = '';
            alertDiv.innerText = '';
            return true;
        }
    })
})