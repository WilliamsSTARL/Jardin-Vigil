async function obtenerUsuarios() {
    try {
        const response = await fetch('http://127.0.0.1:5000/obtener_usuarios', {
            headers: { 'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const usuarios = data.map(usuario => ({
            id_usuario: usuario.id_usuario,
            nombre: usuario.nombre,
            apellido: usuario.apellido,
            email: usuario.email,
            cargo: usuario.cargo,
            salita_a_cargo: (usuario.cargo === '1' || usuario.cargo.toLowerCase() === 'director') ? 'Todas' : (usuario.salita_a_cargo ? usuario.salita_a_cargo : 'No tiene')
        }));
        return usuarios;
    } catch (error) {
        console.error('Error al obtener usuarios:', error);
    }
}
