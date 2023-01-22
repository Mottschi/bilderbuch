$(document).ready(() => {
    let aufnahmen = [];
    const csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val()

    getRecordings();
    
    function getRecordings() {
        $.ajax({
            url: '/user/aufnahmen/api',
            data: {
    
            },
            type: 'GET',
            dataType: 'json',
        }).done((json)=>{
            aufnahmen = json.aufnahmen;
            drawTable();
        }).fail(()=>{
            alert('Die Aufnahmen konnten nicht geladen werden.')
        })
    }

    function drawTable() {
        let tableContainer = document.getElementById('aufnahmen');

        if (aufnahmen.length === 0) {
            tableContainer.innerText = 'Es wurden noch keine Aufnahmen angelegt.';
            return;
        }

        const table = document.createElement('table');
        table.className += "table table-hover align-middle";
        const thead = table.createTHead();
        
        const hrow = thead.insertRow();

        const headers = ['Bearbeiten', 'Titel', 'Sprache', 'Status', 'Sichtbarkeit', 'Löschen'];

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
            anchorElement.href = aufnahme.edit_url;
            anchorElement.innerHTML=document.getElementById("editPencil").innerHTML;
            anchorElement.className = 'btn btn-outline-primary'         
            editCell.appendChild(anchorElement)

            let titleCell = row.insertCell()
            const imgElement = document.createElement('img');
            imgElement.src = `/static/${aufnahme.thumbnail}`;
            imgElement.width=100;

            titleCell.appendChild(imgElement);
            titleCell.appendChild(document.createTextNode(` ${aufnahme.title}`));

            row.insertCell().appendChild(document.createTextNode(`${aufnahme.sprache}`));
            row.insertCell().appendChild(document.createTextNode(`${aufnahme.aufnahmen_count}/${aufnahme.seiten_count}`));

            const sichtbarkeitBtn = document.createElement('button');
            sichtbarkeitBtn.innerHTML = document.getElementById("eyeVisible").innerHTML;
            sichtbarkeitBtn.className = (aufnahme.is_public) ? 'btn btn-success' : 'btn btn-danger';

            sichtbarkeitBtn.addEventListener('click', (event)=>{
                $.ajax({
                    url: aufnahme.toggle_publicity_url,
                    data: {csrfmiddlewaretoken: csrfmiddlewaretoken},
                    type: 'POST',
                    dataType: 'json',
                }).done((json)=>{
                    console.log(json)
                    for (let j=0; j<aufnahmen.length;j++) {
                        console.log('cycling through to find the element that was toggled')
                        if (aufnahmen[i].id === aufnahme.id) {
                            aufnahmen[i].is_public = json.sichtbarkeit;
                        }
                        sichtbarkeitBtn.className = (json.sichtbarkeit) ? 'btn btn-success' : 'btn btn-danger';
                    }})
                .fail((response)=>{
                    let alert_message;
                    if ('responseJSON' in response) {
                        alert_message = response.responseJSON.error;
                        if (response.responseJSON.reload && confirm(`${alert_message} Es ist möglich, dass die Liste nicht mehr auf dem aktuellen Stand ist, soll die Liste neu vom Server geladen werden?`)) {
                            getRecordings();
                        } else {
                            alert(alert_message);
                        }
                    }
                    else {
                        alert('Das Umschalten der Sichtbarkeit ist fehlgeschlagen!');
                        return;
                    }
                    
                    
                });
            });

            row.insertCell().appendChild(sichtbarkeitBtn);

            const deleteBtn = document.createElement('button');
            deleteBtn.innerHTML = document.getElementById("deleteTrash").innerHTML;
            deleteBtn.className = 'btn btn-outline-danger'

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