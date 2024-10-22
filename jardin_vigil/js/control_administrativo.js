function control_administrativo(){
    document.addEventListener('DOMContentLoaded', () => {
        const cargo = localStorage.getItem('cargo');
    if (cargo !== '1') {
        alert('Esta zona es solo para directivos. Serás redirigido a Noticias.');
            window.location.href = 'noticias.html';
        }
    });
}