$(document).ready(() => {
    // Once document is loaded, attach an event handler to the generate keys button
    // event handler should deactivate the button, contact backend to generate keys, 
    // and play the loading animation until it receives a response
    // the response will include an array with the keys in the 'codes' value
    // this array should then be turned into a blob to generate a text file and automatically download
    console.log('ready')
    
    $('#btnKeygen').click((event)=>{
        // get value from the number input field #id_amount
        inputAmount = $('#id_amount')
        amount = parseInt(inputAmount.val())
        csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val()
        if (isNaN(amount) || amount < 1 || amount > 1000) {
            alert('Bitte geben Sie eine Zahl zwischen 1 und 1000 ein.');
            return;
        }
        
        // Remove the form and replace it with loading animation until we receive the response and overwrite the appdiv html again
        appDiv = $('#app')
        originalForm = appDiv.html()
        appDiv.html('<div class="spinner-border" role="status"></div>')

        // send AJAX request
        $.ajax({
            url: `${location.pathname}/api`,
            data: {
                amount: amount,
                csrfmiddlewaretoken: csrfmiddlewaretoken
            },
            type: 'POST',
            dataType: 'json',
        }).done((json) => {
            // generate the file and download it
            let codes = json.codes.join('\n')
            const a = document.createElement('a')
            const blob = new Blob([codes], {type: 'text/plain'})
            a.href = URL.createObjectURL(blob)
            a.download = `${json.title} - codes.txt`
            a.click()
            URL.revokeObjectURL(a)
            appDiv.html('Die Codes wurden erfolgreich generiert.')
            appDiv.addClass('alert alert-success')
        }).fail(() => {
            alert('Beim Generieren der Keys ist ein Fehler aufgetreten.')
            location.reload()
        })


    })
})