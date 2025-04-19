import textwrap
from abc import ABC
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor <= 0:
            print("Valor inválido para saque.")
            return False
        if valor > self._saldo:
            print("Saldo insuficiente.")
            return False
        self._saldo -= valor
        print(f"Saque de R$ {valor:.2f} realizado com sucesso!")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("Valor inválido para depósito.")
            return False
        self._saldo += valor
        print(f"Depósito de R$ {valor:.2f} realizado com sucesso!")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([
            t for t in self.historico.transacoes if t["tipo"] == Saque.__name__
        ])

        if valor > self._limite:
            print("Valor excede o limite de saque.")
            return False
        if numero_saques >= self._limite_saques:
            print("Limite de saques diários excedido.")
            return False

        return super().sacar(valor)

    def __str__(self):
        return f"Agência: {self.agencia}\nConta: {self.numero}\nTitular: {self.cliente.nome}"


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })


class Transacao(ABC):
    @property
    def valor(self):
        pass

    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


def exibir_menu():
    menu = """
    ================================
    Bem-vindo ao Banco OO!
    Escolha uma operação:
    [d] Depósito
    [s] Saque
    [e] Extrato
    [nu] Novo Usuário
    [nc] Nova Conta
    [lc] Listar Contas
    [q] Sair
    ================================
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    return next((c for c in clientes if c.cpf == cpf), None)


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Cliente não possui contas.")
        return None
    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado.")
        return
    try:
        valor = float(input("Valor do depósito: R$ "))
    except ValueError:
        print("Valor inválido.")
        return
    conta = recuperar_conta_cliente(cliente)
    if conta:
        transacao = Deposito(valor)
        cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado.")
        return
    try:
        valor = float(input("Valor do saque: R$ "))
    except ValueError:
        print("Valor inválido.")
        return
    conta = recuperar_conta_cliente(cliente)
    if conta:
        transacao = Saque(valor)
        cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado.")
        return
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    print("\n========= EXTRATO =========")
    for transacao in conta.historico.transacoes:
        try:
            print(f"{transacao['data']} - {transacao['tipo']}: R$ {transacao['valor']:.2f}")
        except (TypeError, ValueError):
            print(f"{transacao['data']} - {transacao['tipo']}: VALOR INVÁLIDO")
    print(f"Saldo atual: R$ {conta.saldo:.2f}")
    print("===========================")


def criar_usuario(clientes):
    cpf = input("Informe o CPF: ")
    if filtrar_cliente(cpf, clientes):
        print("Usuário já cadastrado.")
        return
    nome = input("Nome completo: ")
    nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço (logradouro, número - bairro - cidade/UF): ")
    cliente = PessoaFisica(nome, nascimento, cpf, endereco)
    clientes.append(cliente)
    print("Usuário criado com sucesso!")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do titular: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Usuário não encontrado. Cadastre primeiro.")
        return
    conta = ContaCorrente.nova_conta(cliente, numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("Conta criada com sucesso!")


def listar_contas(contas):
    for conta in contas:
        print("=" * 30)
        print(conta)


def main():
    clientes = []
    contas = []
    while True:
        opcao = exibir_menu()
        match opcao:
            case "d":
                depositar(clientes)
            case "s":
                sacar(clientes)
            case "e":
                exibir_extrato(clientes)
            case "nu":
                criar_usuario(clientes)
            case "nc":
                numero_conta = len(contas) + 1
                criar_conta(numero_conta, clientes, contas)
            case "lc":
                listar_contas(contas)
            case "q":
                print("Obrigado por usar o Banco OO. Até logo!")
                break
            case _:
                print("Opção inválida. Tente novamente.")


main()