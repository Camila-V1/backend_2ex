#!/bin/bash

# ============================================================================
# Script para Actualizar CORS en el Backend para Vercel
# ============================================================================
# Ejecutar este script después de desplegar tu frontend en Vercel
# Uso: ./update_cors_for_vercel.sh tu-app.vercel.app

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}  Actualización de CORS para Frontend en Vercel${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

# Verificar que se proporcionó el dominio de Vercel
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Debes proporcionar tu dominio de Vercel${NC}"
    echo ""
    echo -e "${YELLOW}Uso:${NC}"
    echo "  ./update_cors_for_vercel.sh tu-app.vercel.app"
    echo ""
    echo -e "${YELLOW}Ejemplo:${NC}"
    echo "  ./update_cors_for_vercel.sh mi-ecommerce.vercel.app"
    echo ""
    exit 1
fi

VERCEL_DOMAIN=$1
SERVER_IP="98.92.49.243"
SSH_KEY="django-backend-key.pem"
SSH_USER="ubuntu"

echo -e "${GREEN}📝 Configuración:${NC}"
echo "  • Dominio Vercel: https://${VERCEL_DOMAIN}"
echo "  • Servidor Backend: ${SERVER_IP}"
echo ""

# Verificar que existe la clave SSH
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}❌ Error: No se encuentra el archivo ${SSH_KEY}${NC}"
    echo -e "${YELLOW}Asegúrate de estar en la carpeta correcta que contiene la clave SSH${NC}"
    exit 1
fi

echo -e "${YELLOW}🔄 Conectando al servidor...${NC}"

# Crear archivo temporal con la configuración actualizada
cat > /tmp/update_env.sh << EOF
#!/bin/bash
cd /var/www/django-backend

# Backup del archivo .env actual
sudo cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Actualizar ALLOWED_HOSTS
sudo sed -i 's/^ALLOWED_HOSTS=.*/ALLOWED_HOSTS=${SERVER_IP},localhost,127.0.0.1,${VERCEL_DOMAIN}/' .env

# Actualizar o agregar CORS_ALLOWED_ORIGINS
if grep -q "^CORS_ALLOWED_ORIGINS=" .env; then
    sudo sed -i 's|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=https://${VERCEL_DOMAIN},https://${VERCEL_DOMAIN},http://localhost:3000,http://localhost:5173|' .env
else
    echo "CORS_ALLOWED_ORIGINS=https://${VERCEL_DOMAIN},https://${VERCEL_DOMAIN},http://localhost:3000,http://localhost:5173" | sudo tee -a .env
fi

# Si existe CORS_ALLOW_ALL_ORIGINS, cambiar a False
if grep -q "^CORS_ALLOW_ALL_ORIGINS=" .env; then
    sudo sed -i 's/^CORS_ALLOW_ALL_ORIGINS=.*/CORS_ALLOW_ALL_ORIGINS=False/' .env
fi

echo "✅ Configuración actualizada"
EOF

# Copiar y ejecutar el script en el servidor
scp -i "$SSH_KEY" /tmp/update_env.sh ${SSH_USER}@${SERVER_IP}:/tmp/
ssh -i "$SSH_KEY" ${SSH_USER}@${SERVER_IP} "chmod +x /tmp/update_env.sh && /tmp/update_env.sh"

# Limpiar archivo temporal local
rm /tmp/update_env.sh

echo ""
echo -e "${GREEN}✅ Configuración actualizada en el servidor${NC}"
echo ""
echo -e "${YELLOW}🔄 Reiniciando servicios...${NC}"

# Reiniciar Gunicorn
ssh -i "$SSH_KEY" ${SSH_USER}@${SERVER_IP} "sudo systemctl restart gunicorn"
echo -e "${GREEN}  ✓ Gunicorn reiniciado${NC}"

# Reiniciar Nginx
ssh -i "$SSH_KEY" ${SSH_USER}@${SERVER_IP} "sudo systemctl restart nginx"
echo -e "${GREEN}  ✓ Nginx reiniciado${NC}"

echo ""
echo -e "${YELLOW}🔍 Verificando estado de los servicios...${NC}"

# Verificar estado de Gunicorn
GUNICORN_STATUS=$(ssh -i "$SSH_KEY" ${SSH_USER}@${SERVER_IP} "systemctl is-active gunicorn")
if [ "$GUNICORN_STATUS" = "active" ]; then
    echo -e "${GREEN}  ✓ Gunicorn: Activo${NC}"
else
    echo -e "${RED}  ✗ Gunicorn: Inactivo${NC}"
fi

# Verificar estado de Nginx
NGINX_STATUS=$(ssh -i "$SSH_KEY" ${SSH_USER}@${SERVER_IP} "systemctl is-active nginx")
if [ "$NGINX_STATUS" = "active" ]; then
    echo -e "${GREEN}  ✓ Nginx: Activo${NC}"
else
    echo -e "${RED}  ✗ Nginx: Inactivo${NC}"
fi

echo ""
echo -e "${BLUE}============================================================================${NC}"
echo -e "${GREEN}✅ CONFIGURACIÓN COMPLETADA${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo -e "${YELLOW}📋 Resumen de cambios:${NC}"
echo "  • ALLOWED_HOSTS actualizado con: ${VERCEL_DOMAIN}"
echo "  • CORS_ALLOWED_ORIGINS configurado para: https://${VERCEL_DOMAIN}"
echo "  • Servicios reiniciados correctamente"
echo ""
echo -e "${YELLOW}🧪 Prueba tu aplicación:${NC}"
echo "  • Frontend: https://${VERCEL_DOMAIN}"
echo "  • Backend API: http://${SERVER_IP}/api/"
echo "  • Admin Panel: http://${SERVER_IP}/admin/"
echo ""
echo -e "${YELLOW}🔑 Credenciales de prueba:${NC}"
echo "  • Cliente: juan_cliente / password123"
echo "  • Manager: carlos_manager / manager123"
echo "  • Admin: admin / admin123"
echo ""
echo -e "${GREEN}✨ ¡Listo! Tu frontend en Vercel ahora puede conectarse al backend.${NC}"
echo ""
