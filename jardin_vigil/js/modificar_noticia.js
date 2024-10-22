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
        formData.append('titulo', titulo);
        formData.append('contenido', contenido);
        formData.append('fk_usuario', 1);
        formData.append('resumen', resumen);
        if (imagen) {
            formData.append('imagen', imagen, imagen.name);
        }
        const response = await fetch('http://localhost:5000/modificarnoticia', {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
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