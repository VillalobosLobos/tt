let contador = 0;
let total = localStorage.getItem('total') ? parseInt(localStorage.getItem('total')) : 0;
let bien = localStorage.getItem('bien') ? parseInt(localStorage.getItem('bien')) : 0;
const MAX_INTENTOS = 10;

function iniciarReconocimiento() {
    if ('webkitSpeechRecognition' in window) {
        const reconocimiento = new webkitSpeechRecognition();
        reconocimiento.lang = 'es-ES';
        reconocimiento.interimResults = false;
        reconocimiento.maxAlternatives = 1;

        reconocimiento.onresult = function (event) {
            const textoReconocido = event.results[0][0].transcript.toLowerCase().trim();

            var letraActual = document.getElementById('numero').textContent;
            var numero = '';
            var reconoceNumero = '';

            switch (textoReconocido) {
                case 'uno': reconoceNumero = '1'; break;
                case 'dos': reconoceNumero = '2'; break;
                case 'tres': reconoceNumero = '3'; break;
                case 'cuatro': reconoceNumero = '4'; break;
                case 'cinco': reconoceNumero = '5'; break;
                case 'seis': reconoceNumero = '6'; break;
                case 'siete': reconoceNumero = '7'; break;
                case 'ocho': reconoceNumero = '8'; break;
                case 'nueve': reconoceNumero = '9'; break;
                case 'diez': reconoceNumero = '10'; break;
                default: break;
            }

            switch (letraActual) {
                case '1': numero = 'uno'; break;
                case '2': numero = 'dos'; break;
                case '3': numero = 'tres'; break;
                case '4': numero = 'cuatro'; break;
                case '5': numero = 'cinco'; break;
                case '6': numero = 'seis'; break;
                case '7': numero = 'siete'; break;
                case '8': numero = 'ocho'; break;
                case '9': numero = 'nueve'; break;
                case '10': numero = 'diez'; break;
                default: break;
            }

            console.log('Texto reconocido:', textoReconocido);
            console.log('Letra actual: ', letraActual);
            console.log('Contador de intento actual: ', contador);
            console.log('Total (global): ', total);
            console.log('Bien (global): ', bien);

            if (textoReconocido === 'número ' + letraActual || textoReconocido === 'número ' + numero || reconoceNumero == letraActual) {
                bien++;
                total++;
                localStorage.setItem('bien', bien);
                localStorage.setItem('total', total);
                alert('¡Correcto! Dijiste el número ' + letraActual);
            } else {
                contador++;
                if (contador >= 3) {
                    alert("Se acabaron tus intentos para este número.");
                    total++;
                } else {
                    alert('Lo siento, dijiste: ' + textoReconocido);
                    return; // No recarga ni sigue
                }
            }

            // Verifica si ya se hicieron los 10 intentos
            if (total >= MAX_INTENTOS) {
                localStorage.removeItem('total');
                localStorage.removeItem('bien');
                window.location.href = '/acabarNumeros?bien=' + bien;
            } else {
                localStorage.setItem('total', total);
                location.reload(); // Recarga para mostrar un nuevo número
            }
        };

        reconocimiento.onerror = function (event) {
            console.log('Error de reconocimiento de voz:', event.error);
        };

        reconocimiento.start();
    } else {
        alert('Tu navegador no soporta el reconocimiento de voz.');
    }
}
