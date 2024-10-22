async function verificarSesion() {
    try {
        const response = await fetch('http://127.0.0.1:5000/verificarSesion', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            alert('Por favor, inicia sesión para acceder a esta página.');
            window.location.href = 'login.html';
            return;
        }

        const data = await response.json();
        if (!data.isLoggedIn) {
            alert('Por favor, inicia sesión para acceder a esta página.');
            window.location.href = 'login.html';
        } else {
            const userRole = data.role;
            console.log('Usuario logeado con rol:', userRole);
        }
    } catch (error) {
        console.error('Error al verificar la sesión:', error);
        alert('Por favor, inicia sesión para acceder a esta página.');
        window.location.href = 'login.html';
    }
}
