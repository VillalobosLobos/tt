// Esperamos a que cargue el DOM
document.addEventListener('DOMContentLoaded', () => {
    // Seleccionamos todos los ítems del FAQ
    const faqItems = document.querySelectorAll('.faq-item');
  
    faqItems.forEach(item => {
      const questionBtn = item.querySelector('.faq-question');
  
      questionBtn.addEventListener('click', () => {
        // Si este ítem ya está activo, lo cerramos
        if (item.classList.contains('active')) {
          item.classList.remove('active');
        } else {
          // Cerramos los demás ítems
          faqItems.forEach(i => i.classList.remove('active'));
          // Activamos este ítem
          item.classList.add('active');
        }
      });
    });
  });
  