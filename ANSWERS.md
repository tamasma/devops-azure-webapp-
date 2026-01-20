# Respuestas - Ejercicio 4

## 4.1 - Arquitectura y Networking

**¿Por qué es importante separar la infraestructura de aplicaciones (Web App + Function App) de la base de datos en subnets diferentes?**

Porque si un atacante compromete la capa de aplicacion, no puede acceder directamente a la base de datos ya que estan en redes separadas. El trafico entre ellas pasa por el NSG que filtra las conexiones.

**¿Qué ventajas de seguridad y escalabilidad proporciona?**

Seguridad: La base de datos queda aislada y solo es accesible desde la subnet de aplicacion. No esta expuesta a internet.
Escalabilidad: Cada subnet puede crecer de forma independiente sin afectar a la otra. Puedes añadir mas instancias de app sin tocar la red de la BD.

**Describe la regla NSG exacta para que MySQL (puerto 3306) sea accesible solo desde la subnet de aplicación:**

```hcl
security_rule {
  name                       = "Allow-MySQL-Internal"
  priority                   = 103
  direction                  = "Inbound"
  access                     = "Allow"
  protocol                   = "Tcp"
  source_port_range          = "*"
  destination_port_range     = "3306"
  source_address_prefix      = "10.0.1.0/24"
  destination_address_prefix = "10.0.2.0/24"
}
```

---

## 4.2 - Azure Functions y Terraform

**Explica la diferencia entre desplegar una Azure Function mediante Terraform versus usar func publish:**

Terraform crea la infraestructura: el Function App, el Service Plan y el Storage Account. Es como crear la caja vacia donde va a correr la funcion. func publish despliega el codigo Python dentro de esa caja que ya existe.

**¿En qué escenarios usarías cada approach?**

- Terraform: cuando necesitas crear la infraestructura inicial o cambiar su configuracion (SKU, runtime, app settings)
- func publish: cuando solo cambias el codigo de la funcion y la infra ya esta creada

**¿Cómo asegurarías que el código de la Function siempre esté sincronizado con la infraestructura?**

Usando un pipeline con stages separados: primero ejecutas Terraform para asegurar que la infra esta lista, y despues func publish para desplegar el codigo. Ambos en el mismo repo para que vayan juntos.

---

## 4.3 - Pipeline y CI/CD

**Describe por qué agregar un stage separado FUNCTION DEPLOY después de la validación de la infraestructura es una práctica recomendada:**

Porque la infraestructura y el codigo tienen ciclos de vida diferentes. Si el codigo falla puedes hacer rollback sin tocar la infraestructura. Ademas te aseguras de que la infra esta bien desplegada antes de meter codigo encima.

**¿Cómo evitarías desplegar código defectuoso a la Function App?**

Ejecutando tests unitarios y linting antes del despliegue. Si los tests fallan, el pipeline se para y no despliega.

**¿Qué métricas o validaciones deberías incluir?**

- HTTP status 200 en las respuestas
- Tiempo de respuesta aceptable
- Tasa de errores en Application Insights
- Test de conectividad post-despliegue

---

## 4.4 - Seguridad y Monitoreo

**¿Cómo protegerías los secrets (conexiones a base de datos, API keys) en un pipeline de Azure DevOps que despliega tanto Web Apps como Functions?**

Guardando los secrets en Azure Key Vault y usando Variable Groups marcados como secretos en Azure DevOps. Los valores se enmascaran en los logs y nunca quedan expuestos en el codigo.

**¿Qué rol juega Application Insights en la validación post-despliegue de la Function App?**

Permite monitorear en tiempo real los requests, errores y latencia despues del despliegue. Si algo falla con el nuevo codigo lo detectas inmediatamente viendo picos de errores o degradacion del rendimiento.
