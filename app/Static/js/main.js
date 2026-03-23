// Archivo JS principal

console.log("Sistema de reportes cargado correctamente");

// Ejemplo: alerta al enviar formulario
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    if (form) {
        form.addEventListener("submit", function () {
            alert("Reporte enviado correctamente");
        });
    }
});