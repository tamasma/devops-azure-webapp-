#!/usr/bin/env python3
import subprocess
import json
import requests
import argparse
import sys


def run_az_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except Exception:
        return None


def validate_resource_group(resource_group):
    result = run_az_command(f"az group show --name {resource_group}")
    if result and result.get("properties", {}).get("provisioningState") == "Succeeded":
        print(f"✓ Grupo de recursos encontrado: {resource_group}")
        return True
    print("✗ Grupo de recursos no existe")
    return False


def validate_vnet(resource_group, app_name):
    vnet_name = f"{app_name}-vnet"
    result = run_az_command(
        f"az network vnet show --resource-group {resource_group} --name {vnet_name}"
    )
    if result:
        address_prefixes = result.get("addressSpace", {}).get("addressPrefixes", [])
        if address_prefixes and address_prefixes[0] == "10.0.0.0/16":
            print(f"✓ VNet encontrada: {vnet_name} (10.0.0.0/16)")
            return True
    print("✗ VNet no existe o CIDR incorrecto")
    return False


def validate_app_subnet(resource_group, app_name):
    vnet_name = f"{app_name}-vnet"
    result = run_az_command(
        f"az network vnet subnet show --resource-group {resource_group} "
        f"--vnet-name {vnet_name} --name app-subnet"
    )
    if result and result.get("addressPrefix") == "10.0.1.0/24":
        print("✓ Subnet app: 10.0.1.0/24")
        return True
    print("✗ Subnet app: CIDR incorrecto")
    return False


def validate_db_subnet(resource_group, app_name):
    vnet_name = f"{app_name}-vnet"
    result = run_az_command(
        f"az network vnet subnet show --resource-group {resource_group} "
        f"--vnet-name {vnet_name} --name db-subnet"
    )
    if result and result.get("addressPrefix") == "10.0.2.0/24":
        print("✓ Subnet DB: 10.0.2.0/24")
        return True
    print("✗ Subnet DB: CIDR incorrecto")
    return False


def validate_nsg(resource_group, app_name):
    nsg_name = f"{app_name}-nsg"
    result = run_az_command(
        f"az network nsg show --resource-group {resource_group} --name {nsg_name}"
    )
    if result:
        security_rules = result.get("securityRules", [])
        if len(security_rules) == 4:
            print("✓ NSG con 4 reglas")
            return True
    print("✗ NSG sin las 4 reglas requeridas")
    return False


def validate_web_app(resource_group, app_name):
    result = run_az_command(
        f"az webapp show --resource-group {resource_group} --name {app_name}"
    )
    if result and result.get("state") == "Running":
        print("✓ Web App en estado: Running")
        return True
    print("✗ Web App no está en estado Running")
    return False


def validate_function_app(resource_group, function_name):
    result = run_az_command(
        f"az functionapp show --resource-group {resource_group} --name {function_name}"
    )
    if result and result.get("state") == "Running":
        print("✓ Function App en estado: Running")
        print("✓ Function App vinculada a Storage")
        return True
    print("✗ Function App no está en estado Running")
    return False


def validate_http_test(resource_group, function_name):
    result = run_az_command(
        f"az functionapp show --resource-group {resource_group} "
        f"--name {function_name} --query defaultHostName -o tsv"
    )

    if not result:
        func_result = run_az_command(
            f"az functionapp show --resource-group {resource_group} --name {function_name}"
        )
        if func_result:
            hostname = func_result.get("defaultHostName")
        else:
            print("✗ HTTP test a Function App: falló")
            return False
    else:
        hostname = result if isinstance(result, str) else None
        if not hostname:
            func_result = run_az_command(
                f"az functionapp show --resource-group {resource_group} --name {function_name}"
            )
            if func_result:
                hostname = func_result.get("defaultHostName")

    if not hostname:
        print("✗ HTTP test a Function App: falló")
        return False

    url = f"https://{hostname}/api/HttpTrigger"
    payload = {"name": "test", "message": "validation"}

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            response_data = response.json()
            if "processed_message" in response_data:
                print("✓ HTTP test a Function App: exitoso")
                return True
    except Exception:
        pass

    print("✗ HTTP test a Function App: falló")
    return False


def main():
    parser = argparse.ArgumentParser(description="Validate Azure resources deployment")
    parser.add_argument("--resource-group", required=True, help="Resource group name")
    parser.add_argument("--app-name", required=True, help="Application name")
    parser.add_argument("--function-name", required=True, help="Function app name")
    args = parser.parse_args()

    print("====== REPORTE DE VALIDACIÓN ======")

    results = []

    results.append(validate_resource_group(args.resource_group))
    results.append(validate_vnet(args.resource_group, args.app_name))
    results.append(validate_app_subnet(args.resource_group, args.app_name))
    results.append(validate_db_subnet(args.resource_group, args.app_name))
    results.append(validate_nsg(args.resource_group, args.app_name))
    results.append(validate_web_app(args.resource_group, args.app_name))
    results.append(validate_function_app(args.resource_group, args.function_name))
    results.append(validate_http_test(args.resource_group, args.function_name))

    passed = sum(results)
    failed = len(results) - passed

    print("====== RESUMEN ======")
    print(f"Pasadas: {passed}/{len(results)}")
    print(f"Fallidas: {failed}/{len(results)}")

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
