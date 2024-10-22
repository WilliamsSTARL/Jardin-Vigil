document.getElementById('formNoticia').addEventListener('submit', async (event) => {
    event.preventDefault();
    const titulo = document.getElementById('titulo').value;
    const contenido = document.getElementById('contenido').value;
    const resumen = document.getElementById('resumen').value;
    const imagen = document.getElementById('imagen').files[0];

    try {
        const formData = new FormData();
        formData.append('titulo', titulo);
        formData.append('contenido', contenido);
        formData.append('fk_usuario', 1);
        formData.append('resumen', resumen);
        if (imagen) {
            formData.append('imagen', imagen, imagen.name);
        }

        const response = await fetch('http://localhost:5000/nuevanoticia', {
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
        alert('Noticia enviada exitosamente');
        return datos;
    } catch (error) {
        console.error('Error al insertar nueva noticia:', error);
        alert('Error al enviar la noticia');
    }
});