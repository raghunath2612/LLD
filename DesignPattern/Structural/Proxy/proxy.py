from abc import ABC, abstractmethod
class Account(ABC):
    @abstractmethod
    def withdraw(self, amount: int) -> str:
        pass

    @abstractmethod
    def get_account_no(self) -> int:
        pass

class BankAccount(Account):
    """Created Bank account as the main account"""
    def __init__(self, account_no: int):
        self._account_no = account_no

    def withdraw(self, amount: int) -> str:
        return f"Withdrawn {amount} from Bank Account"

    def get_account_no(self) -> int:
        return self._account_no

class ATMInstance(Account):
    """Made ATM as the proxy for the Bank Account
            to do the operations done by ATM"""
    def __init__(self, bank_account: BankAccount):
        self.bank_account = bank_account

    def withdraw(self, amount: int) -> str:
        self.bank_account.withdraw(amount)
        return f"Withdrawn {amount} from ATM"

    def get_account_no(self) -> int:
        return self.bank_account.get_account_no()


def main():
    bank_account = BankAccount(1232)

    atm = ATMInstance(bank_account)
    print(f"Account no: {atm.get_account_no()}")
    print(atm.withdraw(20))

if __name__ == '__main__':
    main()
