from src.features.payment_management.domain.entities import PaymentType, PaymentStatus

def payment_type_to_str(payment_type: PaymentType) -> str:
    return payment_type.value

def payment_status_to_str(status: PaymentStatus) -> str:
    return status.value 