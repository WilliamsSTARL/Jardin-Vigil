async function obtenerSalitas() {
    try {
        const response = await fetch('http://127.0.0.1:5000/traersalitas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (!data.salitas) {
            console.error('No se recibieron datos válidos');
            return [];
        }
        const salitasProcesadas = data.salitas.map(salita => ({
            id_salita: salita.id_salita,
            nombre_salita: salita.nombre_salita,
            turno_salita: salita.turno_salita,
            informacion_salita: salita.informacion_salita,
            body_bg_color_salita: salita.body_bg_color_salita,
            header_bg_color_salita: salita.header_bg_color_salita,
            color_texto_principal_salita: salita.color_texto_principal_salita,
            url_img_principal: salita.url_img_principal,
            estado: salita.estado
        }));
        return salitasProcesadas;
    } catch (error) {
        console.error('Error al obtener salitas:', error);
    }
}
