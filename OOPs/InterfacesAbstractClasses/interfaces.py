from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass

    @abstractmethod
    def refund(self, transaction_id: int) -> bool:
        pass

    def validate_amount(self, amount: float) -> bool:
        return amount > 0

class CreditCardPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount: float):
        if not self.validate_amount(amount):
            return False
        print(f"Payment processed succesfully with Credit Card {amount}")
        return True

    def refund(self, transaction_id: int) -> bool:
        print("Refund processed succesfully for credit card")
        return True

class PaypalPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount: float) -> bool:
        if not self.validate_amount(amount):
            return False

        print(f"Payment processed succesfully with Paypal {amount}")
        return True

    def refund(self, transaction_id: int):
        print("Refund processed succesfully with Paypal")
        return True

# Method Overriding
def checkout(processor: PaymentProcessor, amount: float) -> bool:
    return processor.process_payment(amount)


credit_card = CreditCardPaymentProcessor()
paypal = PaypalPaymentProcessor()
checkout(credit_card, 100)
checkout(paypal, 200)