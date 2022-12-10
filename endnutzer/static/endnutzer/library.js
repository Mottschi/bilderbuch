$(document).ready(() => {
    let library = document.getElementById('library');

    let allebuecher = [];

    $.ajax({
        url: `${location.pathname}/api`,
        data: {
            
        },
        type: 'GET',
        dataType: 'json',
    }).done((json)=>{
        allebuecher = json.library;
        drawLibrary(allebuecher);
    }).fail(()=>{
        alert('Beim Laden der Bibliothek ist ein Fehler aufgetreten.');
    });

    let minAge = 0;
    let maxAge = 99;
    $('#min_age').val(minAge);
    $('#max_age').val(maxAge);

    let searchTerm = $('#search').val();
    let languageSearchOption = null;

    // Event Handler fuer alters filter
    $('#min_age').change((event)=> {
        let newMinValue = parseInt(event.target.value);
        if (isNaN(newMinValue)) {
            $('#min_age').val(minAge);
            return;
        }
        newMinValue = Math.max(0, newMinValue);
        newMinValue = Math.min(newMinValue, maxAge);
        $('#min_age').val(newMinValue);
        minAge = newMinValue;
        filtern();
    })

    $('#max_age').change((event)=> {
        let newMaxValue = parseInt(event.target.value);
        if (isNaN(newMaxValue)) {
            $('#max_age').val(maxAge);
            return;
        }
        newMaxValue = Math.min(99, newMaxValue);
        newMaxValue = Math.max(newMaxValue, minAge);
        $('#max_age').val(newMaxValue);
        maxAge = newMaxValue;
        filtern();
    })

    $('#search').keyup((event) => {
        searchTerm = event.target.value.toLowerCase();
        filtern();
    })

    $('#language').change((event)=>{
        const option = event.target.value;
        if (option === '') {
            languageSearchOption = null;
        } else {
            languageSearchOption = parseInt(option);
        }
        filtern();
    })

    function filtern() {
        let buecher = allebuecher.filter((buch)=> (buch.age <= maxAge) && (buch.age >= minAge) && searchFilter(buch) && languageFilter(buch));

        drawLibrary(buecher);
    }

    function searchFilter(buch) {
        if (buch.title.toLowerCase().includes(searchTerm)) return true;

        for (let i = 0; i < buch.authors.length; i++) {
            if (buch.authors[i].full_name.toLowerCase().includes(searchTerm)) return true;
        }

        return false;
    }

    function languageFilter(buch) {
        console.log(`language filter '${languageSearchOption}'`);

        console.log(buch.sprachen)
        
        console.log('looking')
        if (languageSearchOption === null) return true;
        console.log('not null, keep looking')
        return buch.sprachen.includes(languageSearchOption);
    }

    function drawLibrary(buecher) {

        library.innerText = '';
        if (buecher.length === 0) {
            library.innerText = 'Es wurden keine Bücher gefunden.';
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
    }

})