function reproducirAudio() {
    var letra = document.getElementById('letra').textContent;
    var audio = new Audio('/static/audio/letras/' + letra + '.mp3');
    audio.play(); // Reproduce el audio
}