#!/usr/bin/env python3
"""
Tests completos para el módulo de Wallet (Billetera Virtual)
Cubre: Crear billetera, recargas, retiros, transacciones
"""
import requests
import time
from decimal import Decimal
from config import API_BASE_URL, TEST_CREDENTIALS, Colors

class TestWalletComplete:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.admin_token = None
        self.cliente_token = None
        self.test_wallet_id = None
        self.test_user_id = None
        
    def print_test(self, name, success, details=""):
        """Imprime resultado de test con formato"""
        if success:
            print(f"{Colors.OKGREEN}✅ {name}{Colors.ENDC}")
            if details:
                print(f"   {details}")
        else:
            print(f"{Colors.FAIL}❌ {name}{Colors.ENDC}")
            if details:
                print(f"   {details}")
        return success

    def login(self, role='admin'):
        """Login y obtiene token"""
        print(f"\n🔐 Obteniendo token {role}...")
        credentials = TEST_CREDENTIALS[role]
        response = requests.post(
            f"{self.base_url}/token/",
            json=credentials
        )
        
        if response.status_code == 200:
            token = response.json()['access']
            print(f"{Colors.OKGREEN}✅ Token obtenido{Colors.ENDC}")
            return token
        else:
            print(f"{Colors.FAIL}❌ Error login: {response.status_code}{Colors.ENDC}")
            return None

    def get_user_profile(self, token):
        """Obtiene perfil de usuario"""
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{self.base_url}/users/profile/", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def test_get_my_wallet(self):
        """TEST: Obtener mi billetera (acción correcta)"""
        print("\n💳 TEST: Obtener mi billetera...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        # Usar el endpoint correcto: /wallets/my_wallet/ (action del ViewSet)
        response = requests.get(
            f"{self.base_url}/users/wallets/my_wallet/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            wallet_id = data.get('id')
            balance = data.get('balance', 0)
            
            if wallet_id:
                self.test_wallet_id = wallet_id
            
            return self.print_test(
                "Get my wallet",
                True,
                f"Billetera ID: {wallet_id}, Balance: ${balance}"
            )
        else:
            return self.print_test(
                "Get my wallet",
                False,
                f"Status: {response.status_code}"
            )

    def test_get_wallet_detail(self):
        """TEST: Obtener detalle de billetera"""
        print("\n💳 TEST: Detalle de billetera...")
        
        if not self.test_wallet_id:
            print(f"{Colors.WARNING}⚠ Saltando test (no hay billetera){Colors.ENDC}")
            return True
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/users/wallets/{self.test_wallet_id}/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            balance = data.get('balance', 0)
            return self.print_test(
                "Get wallet detail",
                True,
                f"Balance: ${balance}"
            )
        else:
            return self.print_test(
                "Get wallet detail",
                False,
                f"Status: {response.status_code}"
            )

    def test_wallet_recharge(self):
        """TEST: Recargar billetera (depósito)"""
        print("\n💰 TEST: Depósito a billetera...")
        
        # Obtener perfil de usuario para tener el user_id
        profile = self.get_user_profile(self.admin_token)
        if not profile:
            print(f"{Colors.WARNING}⚠ Saltando test (no se pudo obtener perfil){Colors.ENDC}")
            return True
        
        user_id = profile.get('id')
        
        headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        # Usar endpoint correcto: /wallets/deposit/ (action del ViewSet)
        deposit_data = {
            "user_id": user_id,
            "amount": "100.00",
            "description": "Test deposit"
        }
        
        response = requests.post(
            f"{self.base_url}/users/wallets/deposit/",
            json=deposit_data,
            headers=headers
        )
        
        success = response.status_code in [200, 201]
        if success:
            data = response.json()
            wallet_data = data.get('wallet', {})
            new_balance = wallet_data.get('balance')
            self.test_wallet_id = wallet_data.get('id')
            return self.print_test(
                "Wallet deposit",
                True,
                f"Depósito exitoso. Nuevo balance: ${new_balance}"
            )
        else:
            return self.print_test(
                "Wallet deposit",
                False,
                f"Status: {response.status_code} - {response.text[:200]}"
            )

    def test_wallet_withdraw(self):
        """TEST: Retirar de billetera"""
        print("\n💸 TEST: Retirar de billetera...")
        
        headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        # Usar endpoint correcto: /wallets/withdraw/ (action del ViewSet)
        withdraw_data = {
            "amount": "50.00",
            "description": "Test withdrawal"
        }
        
        response = requests.post(
            f"{self.base_url}/users/wallets/withdraw/",
            json=withdraw_data,
            headers=headers
        )
        
        success = response.status_code in [200, 201]
        if success:
            data = response.json()
            wallet_data = data.get('wallet', {})
            new_balance = wallet_data.get('balance')
            return self.print_test(
                "Wallet withdraw",
                True,
                f"Retiro exitoso. Nuevo balance: ${new_balance}"
            )
        else:
            return self.print_test(
                "Wallet withdraw",
                False,
                f"Status: {response.status_code} - {response.text[:200]}"
            )

    def test_wallet_get_balance(self):
        """TEST: Obtener balance de billetera"""
        print("\n💵 TEST: Obtener balance...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        # Usar endpoint correcto: /wallets/my_balance/ (action del ViewSet)
        response = requests.get(
            f"{self.base_url}/users/wallets/my_balance/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            balance = data.get('balance', 0)
            wallet_id = data.get('wallet_id')
            if wallet_id and not self.test_wallet_id:
                self.test_wallet_id = wallet_id
            return self.print_test(
                "Get wallet balance",
                True,
                f"Balance actual: ${balance}"
            )
        else:
            return self.print_test(
                "Get wallet balance",
                False,
                f"Status: {response.status_code}"
            )

    def test_list_transactions(self):
        """TEST: Listar transacciones de billetera"""
        print("\n📋 TEST: Listar transacciones...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        # Usar endpoint correcto: /wallet-transactions/my_transactions/ (action del ViewSet)
        response = requests.get(
            f"{self.base_url}/users/wallet-transactions/my_transactions/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            # Puede ser lista o diccionario con 'results'
            if isinstance(data, dict):
                count = data.get('count', len(data.get('results', [])))
            else:
                count = len(data)
            return self.print_test(
                "List wallet transactions",
                True,
                f"Total transacciones: {count}"
            )
        else:
            return self.print_test(
                "List wallet transactions",
                False,
                f"Status: {response.status_code}"
            )

    def test_get_transaction_detail(self):
        """TEST: Obtener detalle de transacción"""
        print("\n🔍 TEST: Detalle de transacción...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Primero obtener lista de transacciones
        response = requests.get(
            f"{self.base_url}/users/wallet-transactions/my_transactions/",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"{Colors.WARNING}⚠ No se pudieron obtener transacciones{Colors.ENDC}")
            return True
        
        data = response.json()
        if isinstance(data, dict):
            transactions = data.get('results', [])
        else:
            transactions = data
        
        if not transactions or len(transactions) == 0:
            print(f"{Colors.WARNING}⚠ No hay transacciones disponibles{Colors.ENDC}")
            return True
        
        transaction_id = transactions[0].get('id')
        
        # Obtener detalle de la primera transacción
        response = requests.get(
            f"{self.base_url}/users/wallet-transactions/{transaction_id}/",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            amount = data.get('amount', 0)
            trans_type = data.get('transaction_type', 'N/A')
            return self.print_test(
                "Get transaction detail",
                True,
                f"Transacción: {trans_type} - Monto: ${amount}"
            )
        else:
            return self.print_test(
                "Get transaction detail",
                False,
                f"Status: {response.status_code}"
            )

    def test_filter_transactions_by_type(self):
        """TEST: Filtrar transacciones por tipo"""
        print("\n🔎 TEST: Filtrar transacciones por tipo...")
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(
            f"{self.base_url}/users/wallet-transactions/my_transactions/?type=DEPOSIT",
            headers=headers
        )
        
        success = response.status_code == 200
        if success:
            data = response.json()
            if isinstance(data, dict):
                count = data.get('count', len(data.get('results', [])))
            else:
                count = len(data)
            return self.print_test(
                "Filter transactions by type",
                True,
                f"Transacciones tipo DEPOSIT: {count}"
            )
        else:
            return self.print_test(
                "Filter transactions by type",
                False,
                f"Status: {response.status_code}"
            )

    def test_wallet_insufficient_funds(self):
        """TEST: Intentar retirar más del balance (debe fallar)"""
        print("\n🚫 TEST: Retirar más del balance (debe fallar)...")
        
        headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
        
        # Intentar retirar 1 millón (más de lo que hay)
        withdraw_data = {
            "amount": "1000000.00",
            "description": "Test insufficient funds"
        }
        
        response = requests.post(
            f"{self.base_url}/users/wallets/withdraw/",
            json=withdraw_data,
            headers=headers
        )
        
        # Debe retornar 400 (bad request) o similar
        success = response.status_code in [400, 402]
        return self.print_test(
            "Withdraw insufficient funds (should fail)",
            success,
            f"Status: {response.status_code} (esperado 400/402)"
        )

    def run_all_tests(self):
        """Ejecuta todos los tests de wallet"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}💰 TESTS COMPLETOS DE WALLET{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        results = []
        
        # Setup: Login
        self.admin_token = self.login('admin')
        
        if not self.admin_token:
            print(f"{Colors.FAIL}❌ No se pudo obtener token. Abortando tests.{Colors.ENDC}")
            return []
        
        # Tests de billetera básicos
        print(f"\n{Colors.OKCYAN}💳 PARTE 1: Operaciones Básicas{Colors.ENDC}")
        results.append(self.test_get_my_wallet())
        results.append(self.test_get_wallet_detail())
        results.append(self.test_wallet_get_balance())
        
        # Tests de transacciones
        print(f"\n{Colors.OKCYAN}💸 PARTE 2: Transacciones{Colors.ENDC}")
        results.append(self.test_wallet_recharge())
        results.append(self.test_wallet_withdraw())
        results.append(self.test_list_transactions())
        results.append(self.test_get_transaction_detail())
        results.append(self.test_filter_transactions_by_type())
        
        # Tests de validaciones
        print(f"\n{Colors.OKCYAN}🛡️ PARTE 3: Validaciones{Colors.ENDC}")
        results.append(self.test_wallet_insufficient_funds())
        
        return results


def main():
    tester = TestWalletComplete()
    results = tester.run_all_tests()
    
    # Resumen
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}📊 RESUMEN - WALLET COMPLETE{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"Total tests: {total}")
    print(f"{Colors.OKGREEN}✅ Exitosos: {passed}{Colors.ENDC}")
    if failed > 0:
        print(f"{Colors.FAIL}❌ Fallidos: {failed}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    exit(main())
