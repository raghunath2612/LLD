from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    """Abstract base class for payment processing"""

    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        """Process a payment - must be implemented"""
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> bool:
        """Process a refund - must be implemented"""
        pass

    def validate_amount(self, amount: float) -> bool:
        """Concrete method - shared validation logic"""
        return amount > 0

class CreditCardProcessor(PaymentProcessor):
    """Concrete implementation for credit card payments"""
    def __init__(self, api_key: str):
        self.api_key = api_key

    def process_payment(self, amount: float) -> bool:
        """Process credit card payment"""
        if not self.validate_amount(amount):
            return False
        print(f"Processing ${amount} via credit card")
        return True

    def refund(self, transaction_id: str) -> bool:
        """Process credit card refund"""
        print(f"Refunding transaction {transaction_id} via credit card")
        return True

class PayPalProcessor(PaymentProcessor):
    """Concrete implementation for PayPal payments"""
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def process_payment(self, amount: float) -> bool:
        """Process PayPal payment"""
        if not self.validate_amount(amount):
            return False
        print(f"Processing ${amount} via PayPal")
        return True

    def refund(self, transaction_id: str) -> bool:
        """Process PayPal refund"""
        print(f"Refunding transaction {transaction_id} via PayPal")
        return True

# Usage - abstraction allows treating all processors the same way
def checkout(processor: PaymentProcessor, amount: float):
    """Function works with any PaymentProcessor implementation"""
    return processor.process_payment(amount)

# All processors can be used interchangeably
credit_card = CreditCardProcessor("api_key_123")
paypal = PayPalProcessor("client_id", "secret")

checkout(credit_card, 100.0)  # Works
checkout(paypal, 100.0)  # Works