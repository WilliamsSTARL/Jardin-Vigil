document.getElementById('formNuevoUsuario').addEventListener('submit', async (event) => {
    event.preventDefault(); // Detiene la recarga de la página

    const cargo = localStorage.getItem('cargo');
    if (cargo !== '1') {
        alert('No tiene autorización para insertar un nuevo usuario.');
        return;
    }

    const nombre = document.getElementById('nombre')?.value || '';
    const apellido = document.getElementById('apellido')?.value || '';
    const email = document.getElementById('email')?.value || '';
    const password = document.getElementById('password')?.value || '';
    const cargoUsuario = document.getElementById('cargo')?.value || '';
    const salita_a_cargo = document.getElementById('salita_a_cargo')?.value || '';

    try {
        const datos = {
            nombre: nombre,
            apellido: apellido,
            email: email,
            password: password,
            cargo: cargoUsuario,
            salita: salita_a_cargo,
        };
        const response = await fetch('http://127.0.0.1:5000/nuevoUsuario', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify(datos)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if(response.status === 200){
            alert('Usuario ingresado correctamente');
            window.location.reload();
        }
        return data;
    } catch (error) {
        console.error('Error al insertar nuevo usuario:', error);
    }
});