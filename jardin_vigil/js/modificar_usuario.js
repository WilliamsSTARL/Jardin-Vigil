function modificarUsuario(id_usuario) {
    const form = document.getElementById('formModificarUsuario');
    form.addEventListener('submit', async (event) => {
        console.log('Formulario enviado');
        event.preventDefault();
        const nombre = document.getElementById('modificarNombre').value;
        const apellido = document.getElementById('modificarApellido').value;
        const email = document.getElementById('modificarEmail').value;
        const cargo = document.getElementById('modificarCargo').value;
        const salita_a_cargo = document.getElementById('modificarSalita').value;
        const password = document.getElementById('modificarPassword').value; 

        const datos = { id_usuario };

        if (nombre) datos.nombre = nombre;
        if (apellido) datos.apellido = apellido;
        if (email) datos.email = email;
        if (cargo) datos.cargo = cargo;
        if (salita_a_cargo) datos.salita_a_cargo = salita_a_cargo;
        if (password) datos.password = password;

        try {
            const response = await fetch('http://127.0.0.1:5000/modificarusuario', {
                method: 'POST',
                body: JSON.stringify(datos),
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const resultado = await response.json();
            alert('Usuario modificado exitosamente');
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalModificar'));
            modal.hide();
            // Reload the page without the user noticing
            location.reload();
            return resultado;
        } catch (error) {
            console.error('Error al modificar el usuario:', error);
            alert('Error al modificar el usuario');
        }
    });
}