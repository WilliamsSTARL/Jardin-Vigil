function modificarNoticia(id_noticia) {
    document.getElementById('formModificarNoticia').addEventListener('submit', async (event) => {
        event.preventDefault();
    const titulo = document.getElementById('modificarTitulo').value;
    const contenido = document.getElementById('modificarContenido').value;
    const resumen = document.getElementById('modificarResumen').value;
    const imagen = document.getElementById('modificarImagen').files[0];

    try {
        const formData = new FormData();
        formData.append('id_noticia', id_noticia);
        const response = await fetch('http://localhost:5000/eliminarnoticia', {
            method: 'POST',
            body: formData
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const datos = await response.json();
        alert('Noticia modificada exitosamente');
        return datos;
    } catch (error) {
        console.error('Error al modificar la noticia:', error);
        alert('Error al modificar la noticia');
    }
});
}