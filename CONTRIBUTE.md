# Contributing to Full-Stack FastAPI React Multi-Tenancy Template

Thank you for your interest in contributing to this project! We welcome contributions from the community and are pleased to have you here.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. We expect all contributors to:

- Be respectful and constructive in discussions
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.13+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- **pnpm** - Frontend package manager
- **uv** - Python package manager (recommended)
- **Docker & Docker Compose** - For running dependencies
- **Git** - Version control

### First-Time Setup

1. **Fork the Repository**
   ```bash
   # Fork the repo on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/full_stack_fastapi_react_template.git
   cd full_stack_fastapi_react_template
   ```

2. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/sajanv88/full_stack_fastapi_react_template.git
   git fetch upstream
   ```

## Development Setup

### Backend Setup

1. **Navigate to Backend Directory**
   ```bash
   cd backend
   ```

2. **Set Up Python Environment**
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   uv pip install -e .
   ```

3. **Configure Environment Variables**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   # Update MongoDB URI, Redis URI, SMTP settings, etc.
   ```

4. **Start Infrastructure Services**
   ```bash
   # From the root directory
   docker-compose -f dev.compose.yaml up -d
   ```
   
   This starts:
   - MongoDB (port 27012)
   - Redis (port 6372)
   - Fake SMTP Server (ports 1023, 1083)
   - Caddy (ports 80, 443)

5. **Run the Backend Server**
   ```bash
   # From backend directory
   uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Run Background Workers (Optional)**
   ```bash
   # Celery worker
   make worker
   
   # Flower (monitoring)
   make flower
   ```

### Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend/app
   ```

2. **Install Dependencies**
   ```bash
   pnpm install
   ```

3. **Start Development Server**
   ```bash
   pnpm dev
   ```

4. **Generate API Client (if backend changes)**
   ```bash
   # Make sure backend is running first
   pnpm generate:api
   ```

## Project Structure

### Backend Architecture (Clean Architecture)

```
backend/
├── api/
│   ├── common/           # Shared utilities and base classes
│   │   ├── base_repository.py
│   │   ├── security.py
│   │   └── utils.py
│   ├── core/             # Application core (config, DI)
│   │   ├── config.py
│   │   └── container.py
│   ├── domain/           # Business logic layer
│   │   ├── entities/     # Domain models
│   │   ├── dtos/         # Data transfer objects
│   │   └── interfaces/   # Repository interfaces
│   ├── infrastructure/   # External integrations
│   │   ├── persistence/  # Database implementations
│   │   ├── messaging/    # Celery, Redis
│   │   ├── externals/    # Third-party services
│   │   └── security/     # Auth implementations
│   ├── interfaces/       # API layer
│   │   ├── api_controllers/  # FastAPI endpoints
│   │   ├── middlewares/      # Request/response middleware
│   │   └── email_templates/  # Email templates
│   └── usecases/         # Application services
└── tests/                # Test suite
```

### Frontend Architecture

```
frontend/app/src/
├── api/              # Generated API client
├── components/       # Reusable React components
├── hooks/            # Custom React hooks
├── lib/              # Utility functions
└── assets/           # Static assets
```

## Development Workflow

### Creating a New Feature

1. **Create a Feature Branch**
   ```bash
   git checkout -y main
   git pull upstream main
   git checkout -b feature/your-feature-name
   ```

2. **Implement Your Changes**
   - Follow the project's architecture patterns
   - Write tests for new functionality
   - Update documentation as needed

3. **Keep Your Branch Updated**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

4. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests (if applicable)
   cd frontend/app
   pnpm test
   ```

### Backend Development Guidelines

#### Adding a New Feature

1. **Define Domain Entity** (if needed)
   - Create in `api/domain/entities/`
   - Use Beanie models for MongoDB documents

2. **Create DTOs**
   - Add to `api/domain/dtos/`
   - Use Pydantic models for validation

3. **Define Repository Interface**
   - Add to `api/domain/interfaces/`
   - Follow existing patterns

4. **Implement Repository**
   - Create in `api/infrastructure/persistence/`
   - Inherit from `BaseRepository`

5. **Create Use Case Service**
   - Add to `api/usecases/`
   - Implement business logic

6. **Add API Controller**
   - Create in `api/interfaces/api_controllers/`
   - Use FastAPI router pattern

7. **Register Dependencies**
   - Update `api/core/container.py`
   - Use Punq for dependency injection

8. **Write Tests**
   - Add to `tests/` with appropriate structure
   - Test endpoints, services, and repositories

#### Example: Adding a New Endpoint

```python
# 1. Domain Entity (api/domain/entities/example.py)
from beanie import Document

class Example(Document):
    name: str
    description: str
    
    class Settings:
        name = "examples"

# 2. DTO (api/domain/dtos/example_dto.py)
from pydantic import BaseModel

class ExampleCreateDTO(BaseModel):
    name: str
    description: str

# 3. Repository Interface (api/domain/interfaces/example_repository.py)
from abc import ABC, abstractmethod

class IExampleRepository(ABC):
    @abstractmethod
    async def create(self, data: ExampleCreateDTO) -> Example:
        pass

# 4. Repository Implementation (api/infrastructure/persistence/example_repository.py)
from api.common.base_repository import BaseRepository

class ExampleRepository(BaseRepository[Example], IExampleRepository):
    async def create(self, data: ExampleCreateDTO) -> Example:
        example = Example(**data.model_dump())
        return await example.insert()

# 5. Use Case Service (api/usecases/example_service.py)
class ExampleService:
    def __init__(self, repository: IExampleRepository):
        self._repository = repository
    
    async def create_example(self, data: ExampleCreateDTO) -> Example:
        return await self._repository.create(data)

# 6. API Controller (api/interfaces/api_controllers/example_controller.py)
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/examples", tags=["Examples"])

@router.post("/", response_model=Example)
async def create_example(
    data: ExampleCreateDTO,
    service: ExampleService = Depends()
):
    return await service.create_example(data)
```

### Frontend Development Guidelines

1. **Component Development**
   - Use TypeScript for all components
   - Follow React best practices and hooks patterns
   - Utilize shadcn/ui components when possible

2. **API Integration**
   - Use the generated API client from `src/api/`
   - Regenerate client after backend changes: `pnpm generate:api`

3. **Styling**
   - Use Tailwind CSS for styling
   - Follow existing design patterns
   - Ensure responsive design (mobile-first)

4. **State Management**
   - Use React hooks for local state
   - Consider context for shared state

## Coding Standards

### Python (Backend)

- **Style**: Follow PEP 8
- **Type Hints**: Use type hints for all function signatures
- **Async**: Use async/await for I/O operations
- **Dependency Injection**: Use Punq container
- **Error Handling**: Use custom exceptions from `api.core.exceptions`
- **Logging**: Use structured logging from `api.common.logging`

```python
# Good example
async def get_user_by_id(self, user_id: str) -> User | None:
    """Retrieve a user by their ID.
    
    Args:
        user_id: The unique identifier of the user
        
    Returns:
        User object if found, None otherwise
        
    Raises:
        NotFoundException: If user does not exist
    """
    user = await User.get(user_id)
    if not user:
        raise NotFoundException(f"User {user_id} not found")
    return user
```

### TypeScript (Frontend)

- **Style**: Follow project ESLint configuration
- **Type Safety**: Avoid `any` types, use proper TypeScript types
- **Components**: Use functional components with hooks
- **Props**: Define explicit prop interfaces

```typescript
// Good example
interface UserCardProps {
  userId: string;
  onEdit?: (id: string) => void;
}

export const UserCard: React.FC<UserCardProps> = ({ userId, onEdit }) => {
  // Component implementation
};
```

### General Guidelines

- Write self-documenting code with clear variable names
- Add comments for complex logic
- Keep functions small and focused (single responsibility)
- Avoid deep nesting (max 3-4 levels)
- Use meaningful commit messages (see below)

## Testing Guidelines

### Backend Testing

1. **Test Structure**
   ```bash
   tests/
   ├── conftest.py           # Shared fixtures
   └── interfaces/           # API endpoint tests
       └── test_*.py
   ```

2. **Writing Tests**
   ```python
   import pytest
   from httpx import AsyncClient
   
   @pytest.mark.asyncio
   async def test_create_user(client: AsyncClient):
       response = await client.post(
           "/api/users",
           json={"email": "test@example.com", "password": "Test@123"}
       )
       assert response.status_code == 201
       assert "id" in response.json()
   ```

3. **Run Tests**
   ```bash
   # Run all tests
   pytest
   
   # Run specific test file
   pytest tests/interfaces/test_user_endpoint.py
   
   # Run with coverage
   pytest --cov=api
   ```

### Frontend Testing

- Write unit tests for utility functions
- Write integration tests for complex components
- Test user interactions and edge cases

## Submitting Changes

### Commit Message Format

Follow conventional commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(auth): add magic link authentication

Implement passwordless login via email magic links
- Add magic link generation endpoint
- Create email template for magic links
- Add token verification logic

Closes #123
```

```
fix(tenant): resolve subdomain routing issue

Fixed bug where subdomain routing was not working for
tenants with hyphenated names.

Fixes #456
```

### Pull Request Process

1. **Ensure Your Code is Ready**
   - All tests pass
   - Code follows style guidelines
   - Documentation is updated
   - Commits are clean and well-formatted

2. **Create Pull Request**
   - Push your branch to your fork
   - Open a PR against the `main` branch
   - Fill out the PR template completely

3. **PR Title Format**
   ```
   [Type] Brief description
   
   Example: [Feature] Add magic link authentication
   Example: [Fix] Resolve subdomain routing issue
   ```

4. **PR Description Should Include**
   - Summary of changes
   - Motivation and context
   - Type of change (feature, bugfix, etc.)
   - How to test the changes
   - Screenshots (for UI changes)
   - Related issues

5. **Review Process**
   - Address review comments promptly
   - Keep discussions focused and respectful
   - Make requested changes in new commits
   - Once approved, maintainers will merge

### What to Include in Your PR

✅ **Do Include:**
- Tests for new functionality
- Documentation updates
- Screenshots for UI changes
- Migration scripts (if database changes)
- Updated dependencies (if needed)

❌ **Don't Include:**
- Unrelated changes
- Commented-out code
- Debug statements or console.logs
- Personal configuration files
- Large binary files

## Reporting Issues

### Before Creating an Issue

1. **Search Existing Issues**
   - Check if the issue already exists
   - Comment on existing issues if you have additional information

2. **Verify the Bug**
   - Ensure it's reproducible
   - Test on the latest version
   - Check if it's environment-specific

### Creating a Good Issue

Use the following template:

```markdown
## Description
Clear description of the issue

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.13]
- Node version: [e.g., 20.x]
- Browser: [e.g., Chrome 120]

## Additional Context
Screenshots, error logs, etc.
```

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `question`: Further information requested

## Development Tips

### Debugging

**Backend:**
```python
# Use built-in debugger
import pdb; pdb.set_trace()

# Or use logging
from api.common.logging import logger
logger.debug("Debug message", extra={"data": data})
```

**Frontend:**
```typescript
// Use React DevTools
// Add debugger statement
debugger;

// Console logging
console.log('Debug:', data);
```

### Common Issues

**MongoDB Connection Issues:**
- Ensure Docker containers are running
- Check MongoDB port (27012) is not in use
- Verify `MONGO_URI` in `.env`

**Redis Connection Issues:**
- Ensure Redis container is running
- Check Redis port (6372) is not in use
- Verify `REDIS_URI` in `.env`

**CORS Issues:**
- Check backend CORS configuration
- Ensure frontend URL is in allowed origins

**API Client Out of Sync:**
- Regenerate API client: `pnpm generate:api`
- Ensure backend is running before generation

## Getting Help

- **Documentation**: Check the README.md for setup instructions
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Tag maintainers for review help

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes (for significant contributions)
- Project documentation

Thank you for contributing to this project! 🎉
