$(document).ready(() => {
    console.log('LOADING')
    $('#btnSubmit').click((event)=>{
        const pw = document.getElementById('id_password').value;
        const pw_comparison = document.getElementById('id_password_comparison').value;

        const comparison = pw === pw_comparison;
        if (!comparison) {
            event.preventDefault();

            let alertDiv = document.getElementById('pw-alert');

            if (!alertDiv) {
                alertDiv = document.createElement('div');
                alertDiv.id = 'pw-alert';
                alertDiv.classList = 'alert alert-danger';
                $('body').prepend(alertDiv);
            }

            alertDiv.innerText = "Die beiden Passwörter stimmen nicht überein!"
            
            return;
        }
    })
})