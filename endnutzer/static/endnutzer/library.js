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
        newMinValue = Math.max(0, newMinValue);
        newMinValue = Math.min(newMinValue, maxAge);
        $('#min_age').val(newMinValue);
        minAge = newMinValue;
        filtern();
    })

    $('#max_age').change((event)=> {
        let newMaxValue = parseInt(event.target.value);
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
            // const colDiv = document.createElement('div');
            // colDiv.classList.add('col');
            // library.appendChild(colDiv);

            // create a div for the card
            const cardDiv = document.createElement('div');
            cardDiv.classList.add('card');
            cardDiv.classList.add('h-100');
            cardDiv.classList.add('text-center');
            cardDiv.classList.add('m-1');
            cardDiv.style.width='18rem';
            cardDiv.style.height='20rem';
            cardDiv.addEventListener('click', ()=>{ window.open(`buch/${buch.id}/abspielen`, '_self'); return false; });
            library.appendChild(cardDiv);



            // create an img for the books thumbnail
            const thumbnailImg = document.createElement('img');
            thumbnailImg.src = `/static/${buch.thumbnail}`;
            thumbnailImg.classList.add('img-fluid');
            // thumbnailImg.addEventListener('click', ()=>{ window.open(`buch/${buch.id}/abspielen`, '_self'); return false; });
            cardDiv.appendChild(thumbnailImg);

            // create a div for the body, to hold the title
            let cardbodyDiv = document.createElement('div');
            cardbodyDiv.classList.add('p-1');
            cardbodyDiv.classList.add('d-flex');
            cardbodyDiv.classList.add('align-items-end');
            cardDiv.appendChild(cardbodyDiv);

            // create a div for the title
            const cardtitleDiv = document.createElement('div');
            cardtitleDiv.classList.add('card-title');
            cardtitleDiv.classList.add('col');
            cardtitleDiv.innerHTML = `<h5>${buch.title}</h5>`;
            cardbodyDiv.appendChild(cardtitleDiv);

            recordAnchor = document.createElement('a');
            recordAnchor.href = `buch/${buch.id}/aufnehmen`;
            cardbodyDiv.appendChild(recordAnchor);



            // create a div for the record button
            const recordButtonDiv = document.createElement('div');
            recordButtonDiv.classList.add('btn');
            recordButtonDiv.classList.add('btn-primary');
            recordButtonDiv.innerHTML=document.getElementById('recordMic').innerHTML;
            recordAnchor.appendChild(recordButtonDiv);

            // // create a div for the body, to hold the links
            // cardbodyDiv = document.createElement('div');
            // cardbodyDiv.classList.add('card-body');
            // cardDiv.appendChild(cardbodyDiv);

            // // create two links for accessing playing / recording functionality
            // let cardoptionsAnchor = document.createElement('a');
            // cardoptionsAnchor.classList.add('card-link');
            // cardoptionsAnchor.href = `buch/${buch.id}/abspielen`;
            // cardoptionsAnchor.innerText = 'Abspielen'
            // cardbodyDiv.appendChild(cardoptionsAnchor);

            // cardoptionsAnchor = document.createElement('a');
            // cardoptionsAnchor.classList.add('card-link');
            // cardoptionsAnchor.href = `buch/${buch.id}/aufnehmen`;
            // cardoptionsAnchor.innerText = 'Aufnehmen'
            // cardbodyDiv.appendChild(cardoptionsAnchor);
        }
    }

})