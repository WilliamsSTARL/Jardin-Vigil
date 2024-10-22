function eliminarUsuario(id_usuario) {
    const confirmacion = confirm('Esta acción es irreversible. ¿Está seguro de que desea eliminar este usuario?');
    if (confirmacion) {
        const datos = { id_usuario };

        fetch('http://127.0.0.1:5000/eliminarusuario', {
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
            alert('Usuario eliminado exitosamente');
            // Recargar la página sin que el usuario lo note
            location.reload();
        })
        .catch(error => {
            console.error('Error al eliminar el usuario:', error);
            alert('Error al eliminar el usuario');
        });
    }
}