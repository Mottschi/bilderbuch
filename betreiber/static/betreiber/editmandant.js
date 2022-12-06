$(document).ready(() => {   
    $('#promoteAdmin').hide()
    $('#selectPromoteAdmin').hide()
    

    if ($('#id_username').val() === '') {
        $('#createAdmin').hide();
        $('#id_username').prop('disabled', true);
        currentManager = $('#selectPromoteAdmin').val()
        $('#setManager').val(currentManager)
    } else {
        createAdmin();
        
    }

    
    $('#btnPromoteAdmin').click(() => {
        console.log('clicked on promote')
        $('#createAdmin').hide()
        $('#promoteAdmin').show()
        $('#id_username').prop('disabled', true)
        $('#selectPromoteAdmin').show()
        $('#setManager').val(currentManager)
        $('#selectPromoteAdmin').val(currentManager).change()
    });

    $('#btnCreateAdmin').click(createAdmin);

    $('#selectPromoteAdmin').change((event)=>{
         $('#setManager').val(event.target.value)
    })

    $('#btnResetForm').click(() => {
        console.log('clicked on reset')
        $('#setManager').val(currentManager)
        $('#createAdmin').hide()
        $('#promoteAdmin').hide()
        $('#selectPromoteAdmin').hide()
        $('#id_username').prop('disabled', true)
    })

    function createAdmin() {
            console.log('clicked on create')
            $('#createAdmin').show()
            $('#id_username').prop('disabled', false)
            $('#selectPromoteAdmin').hide()
            $('#promoteAdmin').hide()
            $('#setManager').val('')
        }
})