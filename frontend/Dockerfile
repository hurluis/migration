# Imagen base ligera con nginx
FROM nginx:alpine

# Elimina configuración por defecto de nginx
RUN rm -rf /usr/share/nginx/html/*
RUN rm /etc/nginx/nginx.conf

# Copia los archivos del frontend al directorio público de nginx
COPY . /usr/share/nginx/html

# Copia la configuración de nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Exponer puerto 80
EXPOSE 80

# Iniciar nginx
CMD ["nginx", "-g", "daemon off;"]