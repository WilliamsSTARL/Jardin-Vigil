document.getElementById('formNuevaSalita').addEventListener('submit', async (event) => {
    event.preventDefault(); // Detiene la recarga de la página

    const nombre_salita = document.getElementById('nombre_salita').value;
    const turno_salita = document.getElementById('turno_salita').value;
    if (turno_salita === "0") {
        alert('Por favor, seleccione un turno válido.');
        return;
    }

    try {
        const datos = {
            nombre_salita: nombre_salita,
            turno_salita: turno_salita,
        };
        const response = await fetch('http://127.0.0.1:5000/nuevasalita', {
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
            alert('Salita ingresada correctamente');
            window.location.reload();
        }
        return data;
    } catch (error) {
        console.error('Error al insertar nueva salita:', error);
    }
});