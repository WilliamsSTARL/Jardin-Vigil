document.getElementById('cerrar_sesion').addEventListener('click', () => {
    const modalHtml = `
        <div class="modal fade" id="cerrarSesionModal" tabindex="-1" aria-labelledby="cerrarSesionModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="cerrarSesionModalLabel">Confirmación de Cierre de Sesión</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ¿Está seguro de que desea cerrar sesión?
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" id="confirmarCerrarSesion">Cerrar Sesión</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const cerrarSesionModal = new bootstrap.Modal(document.getElementById('cerrarSesionModal'));
    cerrarSesionModal.show();

    document.getElementById('confirmarCerrarSesion').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = 'login.html';
    });

    document.getElementById('cerrarSesionModal').addEventListener('hidden.bs.modal', () => {
        document.getElementById('cerrarSesionModal').remove();
    });
});
