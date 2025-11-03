from api.common.utils import get_logger, get_utc_now, get_utc_now
from faker import Faker
from api.core.config import settings
from api.core.container import get_role_service, get_user_service
from api.domain.dtos.user_dto import CreateUserDto, UpdateUserDto
from api.common.enums.gender import Gender
from api.common.seeder_utils import get_seed_roles
from api.domain.dtos.role_dto import CreateRoleDto, UpdateRoleDto
from api.domain.enum.role import RoleType
from api.common.security import hash_it
from api.domain.enum.permission import Permission

fake = Faker()

logger = get_logger(__name__)

async def seed_initial_data():
    if settings.fastapi_env != "development":
        logger.info("Seeding is only allowed in development environment. Skipping seeding.")
        return
    
    if settings.mongo_db_name == "myapp":
        logger.warning("Using default database name 'myapp'. Please change it in production environments.")
    # Add your seeding logic here

    user_repo = get_user_service().user_repository
    role_repo = get_role_service().role_repository

    existing_roles = await role_repo.count()
    roles = get_seed_roles()
    if existing_roles == 0:
        logger.info("Seeding initial data...")
        for role in roles:
            create_role = CreateRoleDto(
                name=role.name,
                description=role.description,
            )
            role_id = await role_repo.create(data=create_role)
            update_role = UpdateRoleDto(
                name=role.name, description=role.description,
                permissions=role.permissions
            )
            await role_repo.update(role_id=str(role_id), data=update_role)
            logger.info(f"Seeded role: {role.name}")
        logger.info("Seeded initial roles.")


    # Example: Create an admin user if not exists
    existing_admin = await user_repo.single_or_none(email=settings.admin_email)
    if existing_admin is None:
        existing_role_admin = await role_repo.single_or_none(name=RoleType.ADMIN)
        create_user = CreateUserDto(
            email=settings.admin_email,
            first_name="Admin",
            last_name="User",
            password=hash_it(settings.admin_password),
            gender=Gender.MALE
        )
        user_id = await user_repo.create(data=create_user)
        logger.info(f"Created admin user with email: {settings.admin_email}")
        update_user = UpdateUserDto(role_id=str(existing_role_admin.id))
        await user_repo.update(user_id=user_id, data=update_user)
        existing_role_admin.permissions.append(Permission.HOST_MANAGE_TENANTS)
        await role_repo.update(role_id=existing_role_admin.id, data=UpdateRoleDto(
            name=existing_role_admin.name,
            description=existing_role_admin.description,
            permissions=existing_role_admin.permissions.copy()
        ))
        logger.info(f"Updated admin user with role: {existing_role_admin.name}")
        logger.info("Seeding completed.")

    # Add bunch of fake users
    existing_users = await user_repo.count()
    if existing_users < 10:
        logger.info("Seeding fake users...")
        existing_role_guest = await role_repo.single_or_none(name=RoleType.GUEST)
        for _ in range(100):
            fake_user = CreateUserDto(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                role_id=existing_role_guest.id,
                gender=fake.random_element(elements=[Gender.MALE.value, Gender.FEMALE.value, Gender.PREFER_NOT_TO_SAY.value, Gender.OTHER.value]),
                password=hash_it("Test@123!"),
            )
            await user_repo.create(data=fake_user)
        logger.info("Seeded fake users.")
    
