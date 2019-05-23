# Python4ABMIpea  - Exercício 2
#
# Professor: Bernardo Furtado
#
# Autora: Marlene Aparecida Argenton
#
#
# 1. Objetivo: criar agentes e interações.


class Investors:
    # cria classe: Investidores
    def __init__(self, idinves):  # indicar um número único para cada investidor
        self.id = idinves
        self.balance = 0
        self.interest = 0

    def deposit(self, amount):
        # depositar recursos
        self.balance -= amount
        return amount

    def get_balance(self):
        return self.balance

    def check_funds(self, amount):
        # verificar recursos
        if self.balance - amount <= 0:
            return False
        else:
            return True

    def withdraw(self, amount):
        # retirar recursos
        self.balance += amount + self.interest
        return self.balance


class Banks:
    # cria a classe: Bancos
    def __init__(self, idbank):  # indicar um número único para cada banco
        self.id = idbank
        self.K = 10000
        self.balance = 0
        self.deposit = 0
        self.loanf = 0
        self.spread = 0
        self.interest = 0

    def get_balance(self):
        self.balance = self.deposit + self.spread - self.loanf - self.interest
        return self.balance

    def check_funds(self, amount):
        # verificar recursos
        if self.balance <= 0:
            return False
        else:
            return amount

    def receive_deposit(self, amount):
        self.balance += amount

    def investor_pay(self, amount, investidor):
        self.balance -= amount
        investidor.deposit(amount)

    def provisionar(self):
        self.loanf += self.balance *.2
        self.balance -= self.balance *.2

    def lending(self, amount, recebedor):
        if self.loanf >= amount:
            self.loanf -= amount
            recebedor.deposit(amount)
        else:
            return False

    def receives_loan(self, amount, investidor):
        self.balance += amount * .7
        self.investor_pay(amount, investidor)


class Firms:
    # cria a classe Firmas
    def __init__(self, idfirms):  # indicar um número unico para cada empresa
        self.firms = idfirms
        self.balance = 0
        self.debt = 0
        print('Agent has {} right now'.format(self.balance))

    def get_loan(self, amount):
        self.balance += amount

    def check_funds(self):
        if self.balance > 0:
            return True
        else:
            return False

    def payment_loan(self, amount):
        self.balance -= self.debt
        # print('Agent has {} fun right now'.format(self, amount))


if __name__ == '__main__':
    i = Investors(0)
    b = Banks(0)
    valor_investir = 10
    if i.check_funds(valor_investir):
        b.receive_deposit(i.deposit(valor_investir))
    print(i.balance)
    print(b.balance)