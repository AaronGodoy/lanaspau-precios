import os
import sys

print("==================================================================")
print("ERROR: EL SCRIPT DE RESETEO DE BASE DE DATOS HA SIDO DESHABILITADO")
print("==================================================================")
print("La aplicacion se encuentra en etapa de produccion. El reseteo ")
print("destructivo de tablas esta estrictamente prohibido para evitar la ")
print("perdida de productos reales y usuarios.")
print("Si necesitas hacer cambios en la BD, utiliza migraciones de Alembic.")
sys.exit(1)
