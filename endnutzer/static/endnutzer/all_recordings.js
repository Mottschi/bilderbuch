$(document).ready(() => {
    let aufnahmen = [];
    const csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val()

    getRecordings();

    function getRecordings() {
        $.ajax({
            url: '/mandant/aufnahmen/api',
            data: {},
            type: 'GET',
            dataType: 'json',
        }).done((json)=>{
            aufnahmen = json.aufnahmen;
            console.log(aufnahmen)
            drawTable();
        }).fail(()=>{
            alert('Die Sprachaufnahmen konnten nicht geladen werden.')
        })
    }

    function drawTable() {
        let tableContainer = document.getElementById('aufnahmen');

        if (aufnahmen.length === 0) {
            tableContainer.innerText = 'Es wurden noch keine Aufnahmen angelegt.';
            return;
        }

        const table = document.createElement('table');
        const thead = table.createTHead();
        const hrow = thead.insertRow();

        const headers = ['Abspielen', 'Buchtitel', 'Nutzer', 'Sprache', 'Löschen'];

        for (let i = 0; i < headers.length; i++) {
            const th = document.createElement('th')
            const text = document.createTextNode(headers[i])
            th.appendChild(text);
            hrow.appendChild(th);
        }

        const tbody = table.createTBody();

        for (let i = 0; i < aufnahmen.length; i++) {
            const aufnahme = aufnahmen[i];
            const row = tbody.insertRow();

            let editCell = row.insertCell();

            const anchorElement = document.createElement('a');
            anchorElement.href = aufnahme.play_url;
            anchorElement.innerText = 'Abspielen';

            editCell.appendChild(anchorElement)

            row.insertCell().appendChild(document.createTextNode(`${aufnahme.title}`));
            
            row.insertCell().appendChild(document.createTextNode(`${aufnahme.sprecher}`));          

            row.insertCell().appendChild(document.createTextNode(`${aufnahme.sprache}`));

            const deleteBtn = document.createElement('button');
            deleteBtn.innerText = 'Löschen';

            deleteBtn.addEventListener('click', ()=>{
                if (!window.confirm('Soll diese Aufzeichnung wirklich gelöscht werden?')) {
                    return;
                }

                $.ajax({
                    url: aufnahme.delete_url,
                    data: {csrfmiddlewaretoken: csrfmiddlewaretoken},
                    type: 'POST',
                    dataType: 'json',
                }).done(()=>{
                    row.remove();
                    })
                .fail((response)=>{
                    let alert_message;
                    if ('responseJSON' in response) 
                        alert_message = response.responseJSON.error;
                    else {
                        alert_message = 'Das Löschen ist fehlgeschlagen!'
                        }
                    if (confirm(`${alert_message} Es ist möglich, dass die Liste nicht mehr auf dem aktuellen Stand ist, soll die Liste neu vom Server geladen werden?`)) {
                        getRecordings();
                    }
                });
            });
            row.insertCell().appendChild(deleteBtn);

            tableContainer.replaceChildren(table);
        }      

        
    }

});