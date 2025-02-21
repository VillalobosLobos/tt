document.addEventListener("DOMContentLoaded", function() {
    // Configurar gráfica de Letras
    var ctxLetras = document.getElementById('graficoLetras').getContext('2d');
    new Chart(ctxLetras, {
        type: 'doughnut',
        data: {
            labels: ['Correctas', 'Incorrectas'],
            datasets: [{
                data: [aciertosLetras, erroresLetras],
                backgroundColor: ['#36A2EB', '#FF6384'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    // Configurar gráfica de Números
    var ctxNumeros = document.getElementById('graficoNumeros').getContext('2d');
    new Chart(ctxNumeros, {
        type: 'doughnut',
        data: {
            labels: ['Correctas', 'Incorrectas'],
            datasets: [{
                data: [aciertosNumeros, erroresNumeros],
                backgroundColor: ['#36A2EB', '#FF6384'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
});
