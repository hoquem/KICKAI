"""
Example usage of the Factory Pattern for service creation.

This demonstrates how the ServiceFactory creates services with proper
dependency injection and how to use them in the application.
"""

from src.core.dependency_container import get_container, initialize_container
from src.features.registry import ServiceFactory


def example_basic_usage():
    """Example of basic factory usage."""
    print("=== Basic Factory Usage ===")
    
    # Initialize the container
    container = initialize_container()
    
    # Get the factory
    factory = container.get_factory()
    
    # Create specific services
    player_services = factory.create_player_registration_services()
    payment_services = factory.create_payment_management_services()
    
    print(f"Created {len(player_services)} player registration services")
    print(f"Created {len(payment_services)} payment management services")
    
    # Access services through the container
    from src.features.player_registration.domain.services.player_registration_service import PlayerRegistrationService
    from src.features.payment_management.domain.services.payment_service import PaymentService
    
    registration_service = container.get_service(PlayerRegistrationService)
    payment_service = container.get_service(PaymentService)
    
    print(f"Registration service: {type(registration_service).__name__}")
    print(f"Payment service: {type(payment_service).__name__}")


def example_lazy_creation():
    """Example of lazy service creation."""
    print("\n=== Lazy Service Creation ===")
    
    container = get_container()
    factory = container.get_factory()
    
    # Services are created only when needed
    print("Creating only team administration services...")
    team_services = factory.create_team_administration_services()
    
    print(f"Created team services: {list(team_services.keys())}")
    
    # Other services remain uncreated until explicitly requested
    print("Other services are not created until needed")


def example_cross_feature_dependencies():
    """Example of handling cross-feature dependencies."""
    print("\n=== Cross-Feature Dependencies ===")
    
    container = get_container()
    factory = container.get_factory()
    
    # Create all services to demonstrate cross-feature dependencies
    all_services = factory.create_all_services()
    
    print(f"Total services created: {len(all_services)}")
    print("Services by feature:")
    
    feature_counts = {}
    for service_name in all_services.keys():
        feature = service_name.split('_')[0] if '_' in service_name else 'other'
        feature_counts[feature] = feature_counts.get(feature, 0) + 1
    
    for feature, count in feature_counts.items():
        print(f"  {feature}: {count} services")


def example_service_retrieval():
    """Example of retrieving services from the container."""
    print("\n=== Service Retrieval ===")
    
    container = get_container()
    
    # Get database interface
    database = container.get_database()
    print(f"Database: {type(database).__name__}")
    
    # Check if services are available
    from src.features.player_registration.domain.services.player_registration_service import PlayerRegistrationService
    from src.features.payment_management.domain.services.payment_service import PaymentService
    
    has_registration = container.has_service(PlayerRegistrationService)
    has_payment = container.has_service(PaymentService)
    
    print(f"Has registration service: {has_registration}")
    print(f"Has payment service: {has_payment}")
    
    if has_registration and has_payment:
        reg_service = container.get_service(PlayerRegistrationService)
        pay_service = container.get_service(PaymentService)
        print(f"Successfully retrieved services: {type(reg_service).__name__}, {type(pay_service).__name__}")


def main():
    """Run all factory pattern examples."""
    print("Factory Pattern Usage Examples")
    print("=" * 50)
    
    try:
        example_basic_usage()
        example_lazy_creation()
        example_cross_feature_dependencies()
        example_service_retrieval()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("This is expected if the actual service implementations don't exist yet.")


if __name__ == "__main__":
    main() 