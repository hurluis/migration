# Imagen base ligera con nginx
FROM nginx:alpine

# Elimina configuración por defecto de nginx
RUN rm -rf /usr/share/nginx/html/*

# Copia los archivos del frontend al directorio público de nginx
COPY . /usr/share/nginx/html
# Exponer puerto 80
EXPOSE 80

# Iniciar nginx
CMD ["nginx", "-g","daemon off;"]