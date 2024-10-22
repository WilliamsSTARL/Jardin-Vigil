function eliminarSalita(id_salita) {
    const confirmacion = confirm('Esta acción es irreversible. ¿Está seguro de que desea eliminar esta salita?');
    if (confirmacion) {
        const datos = { id_salita };

        fetch('http://127.0.0.1:5000/eliminarsalita', {
            method: 'DELETE',
            body: JSON.stringify(datos),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP! estado: ${response.status}`);
            }
            alert('Salita eliminada exitosamente');
            // Recargar la página sin que el usuario lo note
            location.reload();
        })
        .catch(error => {
            console.error('Error al eliminar la salita:', error);
            alert('Error al eliminar la salita');
        });
    }
}