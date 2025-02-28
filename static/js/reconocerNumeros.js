let contador = 0;
let total=localStorage.getItem('total') ? parseInt(localStorage.getItem('total')) : 0;
let bien=localStorage.getItem('bien') ? parseInt(localStorage.getItem('bien')) : 0;

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

            var letraActual = document.getElementById('numero').textContent;
            var numero=0;
            var reconoceNumero=0;

            switch (textoReconocido) {
                case 'uno': reconoceNumero='1';break;
                case 'dos': reconoceNumero='2';break;
                case 'tres': reconoceNumero='3';break;
                case 'cuatro': reconoceNumero='4';break;
                case 'cinco': reconoceNumero='5';break;
                case 'seis': reconoceNumero='6';break;
                case 'siete': reconoceNumero='7';break;
                case 'ocho': reconoceNumero='8';break;
                case 'nueve': reconoceNumero='9';break;
                case 'diez': reconoceNumero='10';break;
                default:
                    break;
            }

            switch (letraActual) {
                case '1': numero='uno';break;
                case '2': numero='dos';break;
                case '3': numero='tres';break;
                case '4': numero='cuatro';break;
                case '5': numero='cinco';break;
                case '6': numero='seis';break;
                case '7': numero='siete';break;
                case '8': numero='ocho';break;
                case '9': numero='nueve';break;
                case '10': numero='diez';break;
                default:
                    break;
            }

            console.log('Texto reconocido:', textoReconocido);
            console.log('Letra actual: numero ', letraActual);
            console.log('Contador: ', contador);
            console.log('Total: ', total);
            console.log('Bien: ', bien);
            // Compara si el texto reconocido es la letra correcta
            if (textoReconocido=='número '+letraActual || textoReconocido=='número '+numero || reconoceNumero==letraActual) {
                contador++;
                total++;
                bien++;
                localStorage.setItem('bien', bien);
                localStorage.setItem('total', total);
                alert('¡Correcto! Dijiste el número ' + letraActual);
                if (total == 10) {
                    localStorage.removeItem('total');
                    localStorage.removeItem('bien');
                    window.location.href = '/acabarNumeros?bien=' + bien;
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
                        window.location.href = '/acabarNumeros?bien=' + bien;
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
