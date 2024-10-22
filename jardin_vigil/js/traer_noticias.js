async function obtenerNoticias() {
    try {
        const response = await fetch('http://127.0.0.1:5000/obtener_noticias');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const noticias = data.map(noticia => ({
            id_noticia: noticia.id_noticia,
            titulo: noticia.titulo,
            contenido: noticia.contenido,
            resumen: noticia.resumen,
            fk_turno: noticia.fk_turno,
            fk_salita: noticia.fk_salita,
            fk_usuario: noticia.fk_usuario,
            fecha_publicacion: noticia.fecha_publicacion,
            image_url: noticia.image_url,
            estado: noticia.estado,
        }));
        return noticias;
    } catch (error) {
        console.error('Error al obtener noticias:', error);
    }
}
