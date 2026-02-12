"""
Simple UseCase: Making older things compatible with newer things structure.
Problem: You have a new system that expects a common interface,
but you need to reuse an existing / legacy class whose interface doesn’t match.
soln: Then we use Adapter pattern"""

from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    """This is the Interface we defined in our project, which is then implemented
            by lot of other payment modes.
    """
    @abstractmethod
    def pay(self, amount: int) -> str:
        pass

class StripePaymentProcessor(PaymentProcessor):
    """Stripe is already respecting our current Payment design.
        There is no issue in this code.
        We might already have such other Payment processors like Credit card, UPI, etc.,
    """
    def pay(self, amount: int) -> str:
        return f'Paid {amount} with Stripe'

class LegacyPaypal:
    """Here LegacyPaypal is not supporting the existing PaymentProcessor Contract.
    Because it is legacy, which might be because it was created long back.
    Here we don't want to change the code for this, but we want it to work as per
        our contract."""
    def pay_using_paypal(self, amount: int) -> str:
        return f'Paid {amount} using Paypal'


class PaypalPaymentProcessor(PaymentProcessor):
    """Here we are adapting paypal with our contract"""
    def __init__(self):
        self.paypal = LegacyPaypal()
    def pay(self, amount: int) -> str:
        return self.paypal.pay_using_paypal(amount)


def main():
    gateway = PaypalPaymentProcessor()
    print(gateway.pay(10))

if __name__ == '__main__':
    main()