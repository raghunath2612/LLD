from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: int) -> None:
        pass

class UPIPayment(PaymentStrategy):
    def pay(self, amount: int) -> None:
        print(f"Paid {amount} using UPI")

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount: int) -> None:
        print(f"Paid {amount} using Credit card")

class PaymentService:
    def __init__(self, payment_strategy: PaymentStrategy):
        self.payment_strategy = payment_strategy

    def pay(self, amount: int) -> None:
        self.payment_strategy.pay(amount)

def main():
    upi = UPIPayment()
    upi_payment_service = PaymentService(upi)
    upi_payment_service.pay(10)

    cc = CreditCardPayment()
    cc_payment_service = PaymentService(cc)
    cc_payment_service.pay(20)

if __name__ == '__main__':
    main()