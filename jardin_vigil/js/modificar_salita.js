document.getElementById('formModificarSalita').addEventListener('submit', async (event) => {
    event.preventDefault(); 
    const idSalita = document.getElementById('formModificarSalita').getAttribute('data-id-salita');
    const idSalitaActual = Number(localStorage.getItem('idSalitaActual'));
    const datos = { 
        id_salita: idSalita || idSalitaActual
    };

    const colorHeader = localStorage.getItem('colorHeader');
    const colorFondo = localStorage.getItem('colorFondo');
    const colorTexto = localStorage.getItem('colorTexto');

    if (colorHeader) datos.header_bg_color_salita = colorHeader;
    if (colorFondo) datos.body_bg_color_salita = colorFondo;
    if (colorTexto) datos.color_texto_principal_salita = colorTexto;

    const campos = [
        { id: 'modificarNombreSalita', key: 'nombre_salita' },
        { id: 'modificarTurnoSalita', key: 'turno_salita' },
        { id: 'modificarEstado', key: 'estado' },
    ];

    campos.forEach(campo => {
        const elemento = document.getElementById(campo.id);
        if (elemento && elemento.value) {
            datos[campo.key] = elemento.value;
        }
    });

    const formData = new FormData();
    for (const key in datos) {
        formData.append(key, datos[key]);
    }

    const inputImagen = document.getElementById('inputImagenPrincipal');
    if (inputImagen && inputImagen.files.length > 0) {
        formData.append('imagen', inputImagen.files[0]);
    }

    try {
        const response = await fetch('http://localhost:5000/modificarsalita', {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (response.ok) {
            alert('Salita modificada exitosamente');
        }
        localStorage.removeItem('colorHeader');
        localStorage.removeItem('colorFondo');
        localStorage.removeItem('colorTexto');
        window.location.reload();
        return data;
    } catch (error) {
        console.error('Error al modificar la salita:', error);
        alert('Error al modificar la salita');
    }
});