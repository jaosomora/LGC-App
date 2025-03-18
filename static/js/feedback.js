/**
 * Funcionalidad para el modal de feedback
 */
document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const modal = document.getElementById('feedback-modal');
    const openButton = document.getElementById('open-feedback-button');
    const closeButton = document.getElementById('close-feedback-button');
    const submitButton = document.getElementById('submit-feedback-button');
    const feedbackForm = document.getElementById('feedback-form');
    const feedbackText = document.getElementById('feedback-text');
    const successMessage = document.getElementById('feedback-success-message');
    const errorMessage = document.getElementById('feedback-error-message');

    // Función para abrir el modal
    function openModal() {
        if (!modal) return;
        modal.classList.remove('hidden');
        // Enfocar el campo de texto
        if (feedbackText) {
            setTimeout(() => feedbackText.focus(), 100);
        }
    }

    // Función para cerrar el modal
    function closeModal() {
        if (!modal) return;
        modal.classList.add('hidden');
        // Limpiar el campo de texto
        if (feedbackText) {
            feedbackText.value = '';
        }
    }

    // Mostrar mensaje temporal
    function showTemporaryMessage(element, duration = 3000) {
        if (!element) return;
        
        // Mostrar el mensaje
        element.classList.remove('hidden');
        
        // Ocultar después de la duración especificada
        setTimeout(() => {
            element.classList.add('hidden');
        }, duration);
    }

    // Enviar feedback
    function sendFeedback() {
        // Validar que hay texto
        if (!feedbackText || feedbackText.value.trim() === '') {
            alert('Por favor, escribe tu feedback antes de enviar.');
            return;
        }

        // Crear objeto FormData
        const formData = new FormData();
        formData.append('feedback', feedbackText.value.trim());

        // Enviar datos mediante fetch - volver a usar el endpoint de correo
        fetch('/enviar_feedback', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            console.log('Feedback enviado con éxito:', data);
            
            // Cerrar modal
            closeModal();
            
            // Mostrar mensaje de éxito
            showTemporaryMessage(successMessage);
        })
        .catch(error => {
            console.error('Error al enviar feedback:', error);
            
            // Mostrar mensaje de error
            showTemporaryMessage(errorMessage);
        });
    }

    // Manejadores de eventos
    if (openButton) {
        openButton.addEventListener('click', openModal);
    }

    if (closeButton) {
        closeButton.addEventListener('click', closeModal);
    }

    if (submitButton) {
        submitButton.addEventListener('click', sendFeedback);
    }

    // Cerrar modal con tecla Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
            closeModal();
        }
    });

    // Cerrar modal al hacer clic fuera del contenido
    if (modal) {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                closeModal();
            }
        });
    }

    // También permitir enviar con Enter en el textarea
    if (feedbackText) {
        feedbackText.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && event.ctrlKey) {
                sendFeedback();
            }
        });
    }
});