async function modificarHorario(idHorario) {
    const datos = { 
        id_horario: idHorario
    };

    const campos = [
        { id: 'inicio_' + idHorario, key: 'hora_inicio' },
        { id: 'fin_' + idHorario, key: 'hora_fin' },
    ];

    campos.forEach(campo => {
        const elemento = document.getElementById(campo.id);
        if (elemento && elemento.value) {
            datos[campo.key] = elemento.value;
        }
    });

    try {
        const response = await fetch('http://127.0.0.1:5000/modificarhorario', {
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
        if (response.ok) {
            alert('Horario modificado exitosamente');
            // Actualizar los elementos en la página sin recargar
            campos.forEach(campo => {
                const elemento = document.getElementById(campo.id);
                const textoElemento = document.getElementById('texto_' + campo.id);
                if (elemento && textoElemento) {
                    textoElemento.textContent = elemento.value;
                    elemento.style.display = 'none';
                    textoElemento.style.display = '';
                }
            });
            const botonGuardar = document.querySelector(`button[onclick="modificarHorario(${idHorario})"]`);
            if (botonGuardar) {
                botonGuardar.style.display = 'none';
            }
        }
        return data;
    } catch (error) {
        console.error('Error al modificar el horario:', error);
        alert('Error al modificar el horario');
    }
}