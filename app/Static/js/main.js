
// HOMEFIX JS PRINCIPAL


console.log("🚀 HomeFix cargado correctamente");
        
// SWEET ALERT TOAST


document.addEventListener("DOMContentLoaded", function () {

    const flashMessage = document.body.dataset.message;
    const flashCategory = document.body.dataset.category;

    if (flashMessage) {

        const Toast = Swal.mixin({

            toast: true,

            position: 'top-end',

            showConfirmButton: false,

            timer: 3000,

            timerProgressBar: true

        });

        Toast.fire({

            icon: flashCategory || 'success',

            title: flashMessage

        });

    }

});

// CONFIRMAR ELIMINAR


document.addEventListener("DOMContentLoaded", function () {

    const formsEliminar = document.querySelectorAll('.form-eliminar');

    formsEliminar.forEach(form => {

        form.addEventListener('submit', function (e) {

            e.preventDefault();

            Swal.fire({

                title: '¿Eliminar reporte?',

                text: 'Esta acción eliminará el reporte y generará el PDF.',

                icon: 'warning',

                showCancelButton: true,

                confirmButtonColor: '#d33',

                cancelButtonColor: '#3085d6',

                confirmButtonText: 'Sí, eliminar',

                cancelButtonText: 'Cancelar'

            }).then((result) => {

                if (result.isConfirmed) {

                    form.submit();

                }

            });

        });

    });

});



// CONFIRMAR ASIGNACIONES

document.addEventListener("DOMContentLoaded", function () {

    const formsAsignar = document.querySelectorAll('.form-asignar');

    formsAsignar.forEach(form => {

        form.addEventListener('submit', function (e) {

            e.preventDefault();

            Swal.fire({

                title: '¿Confirmar asignación?',

                text: 'El reporte será asignado.',

                icon: 'question',

                showCancelButton: true,

                confirmButtonText: 'Asignar',

                cancelButtonText: 'Cancelar'

            }).then((result) => {

                if (result.isConfirmed) {

                    form.submit();

                }

            });

        });

    });

});



// CONFIRMAR LOGOUT


document.addEventListener("DOMContentLoaded", function () {

    const logoutBtn = document.querySelector('.btn-logout');

    if (logoutBtn) {

        logoutBtn.addEventListener('click', function (e) {

            e.preventDefault();

            const url = this.href;

            Swal.fire({

                title: 'Cerrar sesión',

                text: '¿Deseas salir de HomeFix?',

                icon: 'question',

                showCancelButton: true,

                confirmButtonText: 'Cerrar sesión',

                cancelButtonText: 'Cancelar'

            }).then((result) => {

                if (result.isConfirmed) {

                    window.location.href = url;

                }

            });

        });

    }

});

// CONFIRMAR EDICIÓN

document.addEventListener("DOMContentLoaded", function () {

    const formsEditar = document.querySelectorAll('.form-editar');

    formsEditar.forEach(form => {

        form.addEventListener('submit', function (e) {

            e.preventDefault();

            Swal.fire({

                title: 'Guardar cambios',

                text: '¿Deseas actualizar la información?',

                icon: 'question',

                showCancelButton: true,

                confirmButtonText: 'Guardar',

                cancelButtonText: 'Cancelar'

            }).then((result) => {

                if (result.isConfirmed) {

                    form.submit();

                }

            });

        });

    });

});

// LOADER HOMEFIX

document.addEventListener("DOMContentLoaded", function () {

    const formsLoader = document.querySelectorAll('.form-loader');

    formsLoader.forEach(form => {

        form.addEventListener('submit', function () {

            Swal.fire({

                title: 'Procesando...',

                text: 'HomeFix está gestionando la información',

                allowOutsideClick: false,

                didOpen: () => {

                    Swal.showLoading();

                }

            });

        });

    });

});

// ALERTA PDF

document.addEventListener("DOMContentLoaded", function () {

    const botonesPDF = document.querySelectorAll('.btn-pdf');

    botonesPDF.forEach(btn => {

        btn.addEventListener('click', function () {

            Swal.fire({

                icon: 'success',

                title: 'PDF generado correctamente',

                timer: 2000,

                showConfirmButton: false

            });

        });

    });

});