from kickai.features.payment_management.domain.entities import PaymentStatus, PaymentType


def payment_type_to_str(payment_type: PaymentType) -> str:
    return payment_type.value

def payment_status_to_str(status: PaymentStatus) -> str:
    return status.value
