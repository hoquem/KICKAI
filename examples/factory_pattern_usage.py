"""
Example usage of the Factory Pattern for service creation.

This demonstrates how the ServiceFactory creates services with proper
dependency injection and how to use them in the application.
"""

from core.dependency_container import get_container, initialize_container
from features.registry import ServiceFactory
from loguru import logger


def example_basic_usage():
    """Example of basic factory usage."""
    logger.info("=== Basic Factory Usage ===")
    
    # Initialize the container
    container = initialize_container()
    
    # Get the factory
    factory = container.get_factory()
    
    # Create specific services
    player_services = factory.create_player_registration_services()
    payment_services = factory.create_payment_management_services()
    
    logger.info(f"Created {len(player_services)} player registration services")
    logger.info(f"Created {len(payment_services)} payment management services")
    
    # Access services through the container
    from features.player_registration.domain.services.player_registration_service import PlayerRegistrationService
    from features.payment_management.domain.services.payment_service import PaymentService
    
    registration_service = container.get_service(PlayerRegistrationService)
    payment_service = container.get_service(PaymentService)
    
    logger.info(f"Registration service: {type(registration_service).__name__}")
    logger.info(f"Payment service: {type(payment_service).__name__}")


def example_lazy_creation():
    """Example of lazy service creation."""
    logger.info("\n=== Lazy Service Creation ===")
    
    container = get_container()
    factory = container.get_factory()
    
    # Services are created only when needed
    logger.info("Creating only team administration services...")
    team_services = factory.create_team_administration_services()
    
    logger.info(f"Created team services: {list(team_services.keys())}")
    
    # Other services remain uncreated until explicitly requested
    logger.info("Other services are not created until needed")


def example_cross_feature_dependencies():
    """Example of handling cross-feature dependencies."""
    logger.info("\n=== Cross-Feature Dependencies ===")
    
    container = get_container()
    factory = container.get_factory()
    
    # Create all services to demonstrate cross-feature dependencies
    all_services = factory.create_all_services()
    
    logger.info(f"Total services created: {len(all_services)}")
    logger.info("Services by feature:")
    
    feature_counts = {}
    for service_name in all_services.keys():
        feature = service_name.split('_')[0] if '_' in service_name else 'other'
        feature_counts[feature] = feature_counts.get(feature, 0) + 1
    
    for feature, count in feature_counts.items():
        logger.info(f"  {feature}: {count} services")


def example_service_retrieval():
    """Example of retrieving services from the container."""
    logger.info("\n=== Service Retrieval ===")
    
    container = get_container()
    
    # Get database interface
    database = container.get_database()
    logger.info(f"Database: {type(database).__name__}")
    
    # Check if services are available
    from features.player_registration.domain.services.player_registration_service import PlayerRegistrationService
    from features.payment_management.domain.services.payment_service import PaymentService
    
    has_registration = container.has_service(PlayerRegistrationService)
    has_payment = container.has_service(PaymentService)
    
    logger.info(f"Has registration service: {has_registration}")
    logger.info(f"Has payment service: {has_payment}")
    
    if has_registration and has_payment:
        reg_service = container.get_service(PlayerRegistrationService)
        pay_service = container.get_service(PaymentService)
        logger.info(f"Successfully retrieved services: {type(reg_service).__name__}, {type(pay_service).__name__}")


def main():
    """Run all factory pattern examples."""
    logger.info("Factory Pattern Usage Examples")
    logger.info("=" * 50)
    
    try:
        example_basic_usage()
        example_lazy_creation()
        example_cross_feature_dependencies()
        example_service_retrieval()
        
        logger.info("\n" + "=" * 50)
        logger.info("All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        logger.info("This is expected if the actual service implementations don't exist yet.")


if __name__ == "__main__":
    main() 