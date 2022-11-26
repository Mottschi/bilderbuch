$(document).ready(()=>{
    const csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val()
    const buchID = $('#hiddenBuchID').val()

    let seiteID = null;
    let seitenzahl = null;
    $('#id_text').val('');
    $('#id_file').val('');

    let seiten = [];

    function tabelleZeichnen(pages) {
        if (pages.length === 0) {
            const appDiv = $('table')
            appDiv.html('Es wurden noch keine Seiten erstellt.');
            return;
        }
    
        // Create the table
        const headers = ['Seite', 'Vorschau', 'Text', 'Edit', 'Löschen'];
    
        const table = document.createElement('table');
    
        let thead = table.createTHead();
        let row = thead.insertRow();
        for (let i = 0; i < headers.length; i++) {
            const th = document.createElement('th')
            const text = document.createTextNode(headers[i])
            th.appendChild(text);
            row.appendChild(th);
        }
    
        for (let k in pages) {
            const pageNr = pages[k].seitenzahl;
            const text = pages[k].text;
            const imgUrl = pages[k].picture;
            const pageID = pages[k].id;
            
            const row = table.insertRow();
            row.insertCell().appendChild(document.createTextNode(pageNr));
    
            const imgElement = document.createElement('img');
            imgElement.src = `/static/${imgUrl}`;
            imgElement.width = 100;
            imgElement.height = 100;
            row.insertCell().appendChild(imgElement);
    
            row.insertCell().appendChild(document.createTextNode(text));
    
            const editElement = document.createElement('button');
            editElement.innerText='Edit';
            editElement.addEventListener('click', ()=>{
                // load the page data into the form
                seiteID = pageID;
                seitenzahl = pageNr;
                $('#id_text').val(text);
                $('#id_file').val('');
            })
            row.insertCell().appendChild(editElement);
    
            const deleteElement = document.createElement('button');
            deleteElement.innerText = 'Löschen';
            deleteElement.addEventListener('click', ()=>{
                if (window.confirm("Sind sie sicher, dass diese Seite gelöscht werden soll?")) {
                    $.ajax({
                        url: `/betreiber/buch/seiten/delete/${buchID}/${pageID}/`,
                        method: 'DELETE',
                        beforeSend: function(xhr) {
                            xhr.setRequestHeader('X-CSRFToken', csrfmiddlewaretoken)
                        },
                        data: {csrfmiddlewaretoken:csrfmiddlewaretoken},
                        dataType: 'json',
                    }).done((json)=>{
                        let deleteIndex;
                        for (let i = 0; i < seiten.length; i++) {
                            const page = seiten[i];
                            if (page.id === pageID) {
                                deleteIndex = i;
                            } else if (page.seitenzahl > pageNr) {
                                page.seitenzahl--;
                            }
                        }

                        if (pageID === seiteID) {
                            seiteID = null;
                            seitenzahl = null;
                            $('#id_text').val('');
                            $('#id_file').val('');
                        }

                        seiten.splice(deleteIndex, 1);
                        tabelleZeichnen(seiten);
                    }).fail(()=>{
                        alert('Löschung fehlgeschlagen');
                    })
                }
            })
            row.insertCell().appendChild(deleteElement);
        }
    
        $('table').replaceWith(table);
    }

    $.ajax({
        url: `/betreiber/buch/seiten/${buchID}`,
        data: {},
        dataType: 'json',
        method: 'GET',
    }).done((json)=>{
        seiten = json.seiten;
        tabelleZeichnen(seiten);
        
    }).fail(()=>{
        alert('Die Seiten für dieses Buch konnten nicht geladen werden.')
    }).always(()=>{
        
    })


    $('#btnDiscardPage').click((event)=>{
        event.preventDefault();
        $('#id_text').val('');
        $('#id_file').val('');
        seiteID = null;
        seitenzahl = null;
    });

    $('#btnSavePage').click((event)=>{
        event.preventDefault();

        if ($('#id_file').val() === '' && seiteID === null) {
            alert('Bitte Datei auswählen');
            return false;
        };

        let data = new FormData($('#neueSeiteForm').get(0));                
                
        if (seitenzahl === null) {
            method = 'POST';
            url = `/betreiber/buch/seiten/create/${buchID}/`;

        } 
        else {
            method = 'POST';
            url = `/betreiber/buch/seiten/update/${buchID}/${seiteID}/`;
        } 

        $.ajax({
            url: url,
            data: data,
            type: method,
            processData: false,
            contentType: false,
            beforeSend: function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrfmiddlewaretoken)
            },
        }).done((json)=>{
            // update to include the new/updated page
            newPage = json.seite;

            if (seiteID === null) {
                // when we create a new page, it will be added at the end
                seiten.push(newPage)
            } else {
                // when we update, we need to replace the data in the old page with the new data
                let seite = seiten.filter((seite)=>seite.id === seiteID)[0]
                seite.text = newPage.text;
                seite.picture = newPage.picture;
            }
            
            // clean out the form and saved values
            seiteID = null
            seitenzahl = null
            $('#id_text').val('');
            $('#id_file').val('');

            tabelleZeichnen(seiten)
        }).fail(()=>{
            
        })
        return false;
    });
})