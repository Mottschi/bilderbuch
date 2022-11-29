$(document).ready(() => {
    let library = document.getElementById('library');

    $.ajax({
        url: `${location.pathname}/api`,
            data: {
                
            },
            type: 'GET',
            dataType: 'json',
    }).done((json)=>{
        buecher = json.library;
        if (buecher.length === 0) {
            library.html('Es wurden noch keine Bücher der Bibliothek hinzugefügt.')
            return;
        }

        for (let i = 0; i < buecher.length; i++) {
            const buch = buecher[i];

            // create a div of class col-2
            const colDiv = document.createElement('div');
            colDiv.classList.add('col-2');
            library.appendChild(colDiv);

            // create a div for the card
            const cardDiv = document.createElement('div');
            cardDiv.classList.add('card');
            cardDiv.classList.add('h-100');
            cardDiv.classList.add('text-center');
            colDiv.appendChild(cardDiv);

            // create an img for the books thumbnail
            const thumbnailImg = document.createElement('img');
            thumbnailImg.src = `/static/${buch.thumbnail}`;
            cardDiv.appendChild(thumbnailImg);

            // create a div for the body, to hold the title
            let cardbodyDiv = document.createElement('div');
            cardbodyDiv.classList.add('card-body');
            cardDiv.appendChild(cardbodyDiv);

            // create a div for the title
            const cardtitleDiv = document.createElement('div');
            cardtitleDiv.classList.add('card-title');
            cardtitleDiv.innerHTML = `<h5>${buch.title}</h5>`
            cardbodyDiv.appendChild(cardtitleDiv);

            // create a div for the body, to hold the title
            cardbodyDiv = document.createElement('div');
            cardbodyDiv.classList.add('card-body');
            cardDiv.appendChild(cardbodyDiv);

            // create two links for accessing playing / recording functionality
            let cardoptionsAnchor = document.createElement('a');
            cardoptionsAnchor.classList.add('card-link');
            cardoptionsAnchor.href = `buch/${buch.id}/abspielen`;
            cardoptionsAnchor.innerText = 'Abspielen'
            cardbodyDiv.appendChild(cardoptionsAnchor);

            cardoptionsAnchor = document.createElement('a');
            cardoptionsAnchor.classList.add('card-link');
            cardoptionsAnchor.href = `buch/${buch.id}/aufnehmen`;
            cardoptionsAnchor.innerText = 'Aufnehmen'
            cardbodyDiv.appendChild(cardoptionsAnchor);
        }

    }).fail(()=>{
        alert('Beim Laden der Bibliothek ist ein Fehler aufgetreten.');
    })
})