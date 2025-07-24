## Juego Bolirana para arcade


**Descripción**

La implementación y desarrollo de este proyecto, pretende reforzar los conocimientos relacionados con la integración de Hardware “nuevo” en sistemas embebidos Linux, para lo cual, se hace necesario el desarrollo de controladores especializados para que estos sistemas puedan interactuar correctamente con los dispositivos.

**Descripción funcional**

El proyecto se enfoca en el diseño e implementación de un controlador de hardware dedicado para una consola arcade retro personalizada, basada en Raspberry pi zero 2 w como unidad central. El sistema se basará en la detección de eventos de teclado estándar a través de la interfaz GPIO, configurados como entradas en pull-down. El conjunto de pulsadores genera eventos de teclado estándar para la interacción dentro del juego; el botón de encendido y apagado debe tener las siguientes funcionalidades:

- Apagado completo si se mantiene presionado durante 3 segundos.
- Modo de bajo consumo (si el sistema está encendido) y hay pulsación corta.

La pantalla y el sonido se gestionan por la salida HDMI de la tarjeta. 
Se asume que el hardware siempre estará conectado y el controlador debe iniciarse automáticamente al encender el sistema.

El sistema enciende y llega hasta multiuser.target para no cargar el entorno gráfico completo, de modo que solo se ejecute la ventana gráfica del juego mediante xorg. (esto se hace con el fin de optimizar recursos y tener un arranque más rápido)