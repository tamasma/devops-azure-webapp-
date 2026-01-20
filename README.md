# Terraform Deployment - Azure Infrastructure

## Descripcion

Este proyecto despliega una infraestructura en Azure que incluye:
- Red Virtual (VNet) con subnets para aplicacion y base de datos
- Network Security Group (NSG) con reglas de seguridad
- App Service Plan y Web App (Linux)
- Azure Function App con Python 3.11
- Application Insights para monitoreo
- Storage Account para la Function App

## Requisitos Previos

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) >= 2.40
- [Python](https://www.python.org/downloads/) >= 3.11
- [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local) v4
- Cuenta de Azure con permisos de Contributor

## Estructura del Proyecto

```
terraform-deployment/
├── terraform/
│   ├── main.tf              # Recursos principales (RG, App Service, Storage)
│   ├── variables.tf         # Definicion de variables
│   ├── outputs.tf           # Outputs del despliegue
│   ├── network.tf           # Infraestructura de red (VNet, Subnets, NSG)
│   ├── functions.tf         # Azure Function App y App Insights
│   └── terraform.tfvars     # Valores de las variables
├── scripts/
│   └── validate.py          # Script de validacion post-despliegue
├── function-app/
│   ├── HttpTrigger/
│   │   ├── function_app.py  # Codigo de la Azure Function
│   │   └── function_app.json
│   └── requirements.txt
├── azure-pipelines.yml      # Pipeline CI/CD
├── README.md
└── ANSWERS.md               # Respuestas a preguntas de analisis
```

## Despliegue Manual

### 1. Autenticacion con Azure

```bash
az login
az account set --subscription "<SUBSCRIPTION_ID>"
```

### 2. Inicializar Terraform

```bash
cd terraform
terraform init
```

### 3. Validar configuracion

```bash
terraform validate
terraform fmt -check
```

### 4. Planificar despliegue

```bash
terraform plan -out=tfplan
```

### 5. Aplicar despliegue

```bash
terraform apply tfplan
```

### 6. Obtener outputs

```bash
terraform output
```

### 7. Desplegar Azure Function

```bash
cd ../function-app
func azure functionapp publish webapp-dev-function --python
```

### 8. Validar despliegue

```bash
cd ../scripts
pip install requests
python3 validate.py --resource-group webapp-dev-rg --app-name webapp --function-name webapp-dev-function
```

## Despliegue con Azure DevOps

### Variables requeridas

Crear un Variable Group llamado `terraform-variables` con:
- `azureServiceConnection`: Nombre de la Service Connection de Azure
- `resource-group`: webapp-dev-rg
- `app-name`: webapp
- `function-name`: webapp-dev-function
- `location`: eastus
- `backendResourceGroup`: Resource group para el state de Terraform
- `backendStorageAccount`: Storage account para el state
- `backendContainer`: Container para el state

### Ejecucion

El pipeline se ejecuta automaticamente con push a la rama `main`.

## Test de la Azure Function

```bash
curl -X POST https://webapp-dev-function.azurewebsites.net/api/HttpTrigger \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "message": "hello"}'
```

Respuesta esperada:
```json
{
  "id": "uuid-generado",
  "timestamp": "2024-01-01T00:00:00.000000",
  "processed_message": "Hello test, your message 'hello' has been processed"
}
```

## Limpieza

```bash
cd terraform
terraform destroy
```
