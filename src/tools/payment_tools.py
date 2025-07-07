from src.services.interfaces.payment_service_interface import PaymentType, PaymentStatus

def payment_type_to_str(payment_type: PaymentType) -> str:
    return payment_type.value

def payment_status_to_str(status: PaymentStatus) -> str:
    return status.value 