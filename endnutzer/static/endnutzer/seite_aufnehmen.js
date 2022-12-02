$(document).ready(() => {
    const audio = document.getElementById('audio');
    csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val()

    const btnPlay = $('#btnPlay');
    if (audio.src === '')  btnPlay.hide();

    const btnRecord = $('#btnRecord');

    const btnStopRecording = $('#btnStopRecord');
    btnStopRecording.hide()

    $('#btnPlay').click(()=>{
        audio.play()
    })

    let chunks= [];
    let mimeType = null;

    const types = [
        "audio/webm",
        "audio/mpeg",
        "audio/mp3",
        "audio/mp4",
        "audio/wav",
        "audio/ogg",
        "audio/mpeg3",
        "audio/3gpp"
    ];

    // Find first mimeType that is supported by the browser and set it as mimeType
    mimeType = types.filter(MediaRecorder.isTypeSupported)[0];

    const options = {
        mimeType: mimeType,
        type: mimeType,
      }

    if (!mimeType) {
        alert("Kein gueltiges Audioformat gefunden");
        return;
    }
    
    $('#btnRecord').click(aufnahmeStarten)

    async function aufnahmeStarten() {
        btnPlay.hide()
        btnRecord.hide()
        btnStopRecording.show()
        btnStopRecording.click(aufnahmeStoppen)

        // start recording
        let stream = null;
        const constraints = {
            audio: true,
            video: false,
            mimeType: mimeType
        }
        try {
        stream = await navigator.mediaDevices.getUserMedia(constraints)
        } catch (error) {
        $('#btnPlay').prop('disabled', false)
        return;
        }
        let mediaRecorder = new MediaRecorder(stream, options);

        mediaRecorder.addEventListener("dataavailable", handleDataAvailable);
        mediaRecorder.addEventListener("stop", onStop);

        mediaRecorder.start();

        // necessary helper functions
        function handleDataAvailable(data) {
            chunks.push(data.data)
        }

        function aufnahmeStoppen() {
            mediaRecorder.stop()
        }

        function onStop() {
            const blob = new Blob(chunks, options);
            chunks = [];
            const audioURL= window.URL.createObjectURL(blob)
            
            //once done recording, send audio to backend:
            const formdata = new FormData();
            formdata.append('filename', 'test.webm')
            formdata.append('file', blob);
            formdata.append('csrfmiddlewaretoken', csrfmiddlewaretoken)

            $.ajax({
                url: `${location.pathname}/api`,
                data: formdata,
                type: 'POST',
                dataType: 'json',
                processData: false,
                contentType: false,
            }).done(()=>{
                audio.src = audioURL;
                audio.type = mimeType;
                btnPlay.show()
            }).fail(()=>{
                alert('Die Sprachaufnahme konnte nicht gespeichert werden.')
            }).always(()=>{
                btnRecord.show()
                btnStopRecording.hide()
            })
        }
    }

})