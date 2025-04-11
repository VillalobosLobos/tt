// Variables globales
let contador = 0;
let total = localStorage.getItem('total') ? parseInt(localStorage.getItem('total')) : 0;
let bien = localStorage.getItem('bien') ? parseInt(localStorage.getItem('bien')) : 0;
const MAX_INTENTOS = 10;

// Mensajes de error
const msjError = [
    "¡Buen intento! No te preocupes, a veces necesitamos un poco más de práctica.",
    "¡Uy! Parece que este número es muy difícil. Pero tú puedes con él.",
    "Muy bien, a veces aprender toma tiempo, y está bien.",
    "¡Estás aprendiendo mucho! A veces no sale a la primera, pero cada intento te hace más fuerte.",
    "No fue está vez, pero intenta a la otra"
];

const msjCorre = [
    "¡Muy bien! ¡Eres un campeón! ", 
    "¡Sííí! ¡Dijiste el número correcto!", 
    "¡Eso fue perfecto! ¡Bravo!", 
    "¡Número correcto! ¡Eres asombroso!", 
    "¡Fantástico! ¡Estás aprendiendo mucho!"
];

function iniciarReconocimiento() {
  if ('webkitSpeechRecognition' in window) {
    const reconocimiento = new webkitSpeechRecognition();
    reconocimiento.lang = 'es-ES';
    reconocimiento.interimResults = false;
    reconocimiento.maxAlternatives = 1;

    // Seleccionamos el botón de micrófono
    const btnMicro = document.querySelector('.btn-micro');
    // Añadimos la clase para cambiar el fondo a rojo
    btnMicro.classList.add('active');

    reconocimiento.onresult = function (event) {
      const textoReconocido = event.results[0][0].transcript.toLowerCase().trim();
      const letraActual = document.getElementById('numero').textContent;
      let numero = '';
      let reconoceNumero = '';

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

      // Lógica de comparación
      if (textoReconocido === 'número ' + letraActual || textoReconocido === 'número ' + numero || reconoceNumero === letraActual) {
        bien++;
        total++;
        localStorage.setItem('bien', bien);
        localStorage.setItem('total', total);
        let indice = Math.floor(Math.random() * msjCorre.length);
        mostrarMensajeEnPantalla('✅ ' + msjCorre[indice], true);
        const audio = new Audio('/static/audio/CorreNumeros/' + (indice + 1) + ".mp3");
        audio.play();

      } else {
        contador++; // Incrementar contador en cada intento incorrecto
        if (contador >= 3) {
          let indice = Math.floor(Math.random() * msjError.length);
          mostrarMensajeEnPantalla('❌ ' + msjError[indice], false);
          const audio = new Audio('/static/audio/ErrorNumeros/' + (indice + 1) + ".mp3");
          audio.play();
          total++;
        } else {
          mostrarMensajeEnPantalla('❌ Lo siento, dijiste: "' + textoReconocido + '"', false);
          return;
        }
      }

      // Verifica si ya se hicieron los 10 intentos
      if (total >= MAX_INTENTOS) {
        localStorage.removeItem('total');
        localStorage.removeItem('bien');
        setTimeout(() => {
          window.location.href = '/acabarNumeros?bien=' + bien;
        }, 5000);
      } else {
        localStorage.setItem('total', total);
        setTimeout(() => {
          location.reload();
        }, 5000);
      }
    };

    // Cuando finaliza el reconocimiento, retiramos la clase para restaurar el fondo original
    reconocimiento.onend = function () {
      btnMicro.classList.remove('active');
    };

    reconocimiento.onerror = function (event) {
      console.error('Error de reconocimiento de voz:', event.error);
      btnMicro.classList.remove('active');
    };

    reconocimiento.start();
  } else {
    alert('Tu navegador no soporta el reconocimiento de voz.');
  }
}

// Función para mostrar mensajes en pantalla
function mostrarMensajeEnPantalla(texto, esCorrecto) {
  const mensajeDiv = document.getElementById("mensajeError");

  // Limpiar mensaje anterior
  mensajeDiv.innerText = texto;

  // Cambiar estilo según si es correcto o incorrecto
  if (esCorrecto) {
    mensajeDiv.className = "correcto";
  } else {
    mensajeDiv.className = "incorrecto";
  }

  mensajeDiv.style.display = "block"; // Mostrar mensaje

  // Ocultar el mensaje después de unos segundos
  setTimeout(() => {
    mensajeDiv.style.display = "none";
  }, 5000); // 6 segundos
}
