self.addEventListener('fetch', function(event) {
    if (event.request.url.endsWith('/manifest.json')) {
        event.respondWith(
            fetch('manifest.json') // Reemplaza '/ruta/a/tu/manifest.json' con la ubicación de tu manifest.json personalizado
            .then(function(response) {
                return response;
            })
            .catch(function(error) {
                console.error('Error fetching manifest:', error);
                // Devuelve una respuesta de error personalizada aquí si lo deseas
                return new Response('<h1>Error al cargar el manifiesto</h1>', {
                    headers: {'Content-Type': 'text/html'}
                });
            })
    );
    } else {
      // Continúa con el comportamiento predeterminado del Service Worker para otras solicitudes
    event.respondWith(
        fetch(event.request)
        .then(function(response) {
            return response;
        })
        .catch(function(error) {
            console.error('Error fetching resource:', error);
            // Devuelve una respuesta de error personalizada aquí si lo deseas
            return new Response('<h1>Error al cargar la página</h1>', {
                headers: {'Content-Type': 'text/html'}
            });
        })
    );
    }
});
