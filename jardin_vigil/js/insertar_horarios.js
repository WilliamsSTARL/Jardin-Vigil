document.getElementById('formHorarios').addEventListener('submit', async (event) => {
    event.preventDefault();
    const idSalita = document.getElementById('formHorarios').getAttribute('data-id-salita');
    console.log('ID Salita:', idSalita); // Verifica que el idSalita no sea null
    // Obtener días seleccionados
    const diasSeleccionados = [];
    ['dia_semana1', 'dia_semana2', 'dia_semana3', 'dia_semana4', 'dia_semana5'].forEach(function(id) {
        const checkbox = document.getElementById(id);
        if (checkbox.checked) {
            diasSeleccionados.push(checkbox.value);
        }
    });

    const hora_inicio = document.getElementById('hora_inicio').value;
    const hora_fin = document.getElementById('hora_fin').value;

    try {
        const datos = {
            id_salita: idSalita,
            dia_semana: diasSeleccionados,
            hora_inicio: hora_inicio,
            hora_fin: hora_fin
        };

        const response = await fetch('http://127.0.0.1:5000/nuevoHorario', {
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
            alert('Horario ingresado correctamente');
            window.location.reload();
        }
        return data;
    } catch (error) {
        console.error('Error al insertar nuevo horario:', error);
    }
});
