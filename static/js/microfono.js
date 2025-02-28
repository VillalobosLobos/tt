let contador = 0;
let total = localStorage.getItem('total') ? parseInt(localStorage.getItem('total')) : 0;
let bien = localStorage.getItem('bien') ? parseInt(localStorage.getItem('bien')) : 0;

function iniciarReconocimiento() {
    // Verifica si el navegador soporta la API de reconocimiento de voz
    if ('webkitSpeechRecognition' in window) {
        // Crea una nueva instancia de SpeechRecognition
        const reconocimiento = new webkitSpeechRecognition();
        reconocimiento.lang = 'es-ES';  // Configura el idioma (español)
        reconocimiento.interimResults = false;  // Solo devolverá el resultado final, no resultados intermedios
        reconocimiento.maxAlternatives = 1;  // Máximo de alternativas a devolver

        // Este evento se dispara cuando se reconoce una voz
        reconocimiento.onresult = function (event) {
            // Obtén el resultado (primera alternativa)
            const textoReconocido = event.results[0][0].transcript;

            // Muestra lo que se dijo en consola
            console.log('Texto reconocido:', textoReconocido);
            console.log('Contador: ', contador);
            console.log('Total: ', total);
            console.log('Bien: ', bien);

            var letraActual = document.getElementById('letra').textContent;

            // Compara si el texto reconocido es la letra correcta
            if (textoReconocido.toLowerCase() === 'letra ' + letraActual.toLowerCase() || textoReconocido.toLowerCase() === letraActual.toLowerCase()) {
                contador++;
                total++;
                bien++;
                localStorage.setItem('bien', bien);
                localStorage.setItem('total', total);
                alert('¡Correcto! Dijiste la letra ' + letraActual);
                if (total == 10) {
                    localStorage.removeItem('total');
                    localStorage.removeItem('bien');
                    window.location.href = '/acabarActividades?bien=' + bien;
                    return; 
                }
                location.reload(); // Recarga la página después del alert
            } else {
                contador++;
                if (contador == 3) {
                    total++;
                    localStorage.setItem('total', total);
                    alert("Se acabaron tus intentos");
                    if (total == 10) {
                        localStorage.removeItem('total');
                        window.location.href = '/acabarActividades?bien=' + bien;
                        return; 
                    }
                    location.reload();
                }else{
                    localStorage.setItem('total', total);
                alert('Lo siento, dijiste: ' + textoReconocido);
                }
            }
        };

        // Este evento se dispara si ocurre un error
        reconocimiento.onerror = function (event) {
            console.log('Error de reconocimiento de voz:', event.error);
        };

        // Inicia el reconocimiento de voz
        reconocimiento.start();
    } else {
        alert('Tu navegador no soporta el reconocimiento de voz.');
    }
}
