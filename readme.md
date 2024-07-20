# Manejador de Tareas con Flask, PyDAL, HTMX y Bulma

Este proyecto es un manejador de tareas web desarrollado con Flask, utilizando PyDAL como ORM para la gestión de la base de datos. La interfaz de usuario está mejorada con HTMX para interacciones dinámicas y estilizada con Bulma CSS. Además, se utiliza Font Awesome para los iconos.

## Características

- Crear, actualizar y eliminar tareas (CRUD)
- Interfaz de usuario responsiva y moderna con Bulma CSS
- Interacciones dinámicas sin recarga de página completa gracias a HTMX
- Iconos atractivos de Font Awesome
- Base de datos gestionada con PyDAL

## Requisitos

- Python 3.7+
- Flask
- PyDAL
- HTMX (incluido via CDN)
- Bulma CSS (incluido via CDN)
- Font Awesome (incluido via CDN)

## Instalación

1. Clona este repositorio:   
```
git clone https://github.com/jbenitez05/tasks_list.git
cd tasks_list
```
2. Crea un entorno virtual y actívalo:  
``` 
python -m venv venv
source venv/bin/activate 
```
3. Instala las dependencias:   
```
pip install -r requirements.txt
```
4. Configura la app en `private/appconfig.ini` o renombra `private/appconfig.ini.example`.
5. Inicia la aplicación:   
```
python3 run.py
```
6. Abre tu navegador y visita `http://localhost:5000`.

## Uso

- La página principal muestra la lista de tareas.
- Usa el formulario para agregar nuevas tareas.
- Haz clic en los iconos junto a cada tarea para editarla o eliminarla.

## Contribuir

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios mayores antes de crear un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT.