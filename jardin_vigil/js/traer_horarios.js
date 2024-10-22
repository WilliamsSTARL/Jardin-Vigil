async function traerHorarios() {
    try {
        const response = await fetch('http://127.0.0.1:5000/traerHorarios', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const horarios = data.map(horario => ({
            id_horario: horario.id_horario,
            fk_salita: horario.fk_salita,
            dia_semana: horario.dia_semana,
            hora_inicio: horario.hora_inicio,
            hora_fin: horario.hora_fin,
        }));
        return horarios;
    } catch (error) {
        console.error('Error al obtener horarios:', error);
    }
}
