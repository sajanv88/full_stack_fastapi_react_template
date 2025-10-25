from api.infrastructure.persistence.repositories.payment_repository_impl import  PaymentRepository


class BillingRecordService:
    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository: PaymentRepository = payment_repository
    