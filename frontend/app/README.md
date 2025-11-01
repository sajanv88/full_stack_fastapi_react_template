# Frontend Application

A modern React TypeScript application built with Vite, featuring a comprehensive UI component library, authentication, multi-tenant support, and AI chat capabilities.

## 🎯 Overview

This frontend application provides a complete user interface for the full-stack template, featuring:

- **Modern React 19** with TypeScript for type safety
- **Vite** for fast development and optimized builds
- **Tailwind CSS 4** with shadcn/ui components for consistent design
- **React Router 7** for client-side navigation
- **React Hook Form** with Zod validation for forms
- **Auto-generated API clients** from backend OpenAPI specifications

## 🏗️ Project Structure

```
src/
├── api/                   # Auto-generated API client
│   ├── models/            # TypeScript models from backend
│   ├── services/          # API service classes
│   └── core/              # Core API utilities
├── components/
│   ├── features/         # Feature-specific components
│   │   ├── ai-chat/      # AI chat interface
│   │   ├── auth/         # Authentication components
│   │   ├── dashboard/    # Dashboard components
│   │   ├── profile/      # User profile management
│   │   ├── roles/        # Role management
│   │   ├── tenant/       # Tenant management
│   │   └── users/        # User management
│   ├── layouts/          # Page layout components
│   │   ├── default-layout.tsx
│   │   └── dashboard-sidebar-layout.tsx
│   ├── providers/        # React context providers
│   │   └── auth-provider.tsx
│   ├── shared/           # Reusable components
│   │   ├── footer.tsx
│   │   ├── loading.tsx
│   │   └── list-*.tsx
│   └── ui/               # shadcn/ui base components
├── hooks/                # Custom React hooks
├── lib/                  # Utility functions
│   ├── utils.ts         # General utilities
│   └── image-utils.ts   # Image processing utilities
└── assets/              # Static assets
```

## 🚀 Getting Started

### Prerequisites

- Node.js 22+ 
- pnpm (recommended) or npm
- Backend API running on `http://localhost:8000`

### Installation

1. **Install Dependencies**:
   ```bash
   pnpm install
   ```

2. **Generate API Client** (Backend must be running):
   ```bash
   pnpm run generate:api # You may have to change it to localhost:8000.. Check the package.json 
   ```

3. **Start Development Server**:
   ```bash
   pnpm dev
   ```

   The application will be available at: http://localhost:3000

## 📜 Available Scripts

```bash
# Development
pnpm dev                    # Start development server (port 3000)
pnpm build                  # Build for production
pnpm preview                # Preview production build
pnpm lint                   # Run ESLint

# API Integration
pnpm run generate:api       # Generate TypeScript API client from backend
```

## ⚙️ Configuration

### Vite Configuration

The `vite.config.ts` includes:

- **Development Server**: Runs on port 3000
- **API Proxy**: Routes `/api/*` to backend at `http://localhost:8000`
- **Path Aliases**: `@/*` resolves to `src/*`
- **Build Output**: Builds to `../../backend/api/ui` for integrated deployment
- **Tailwind Integration**: Native Tailwind CSS 4 support

### TypeScript Configuration

- **Strict Mode**: Full TypeScript strict mode enabled
- **Path Mapping**: Absolute imports with `@/` prefix
- **Modern Target**: ES2022 for optimal performance

## 🎨 UI Components & Design System

### Component Library

- **shadcn/ui**: High-quality, accessible React components
- **Radix UI**: Unstyled, accessible primitives
- **Lucide React**: Beautiful SVG icons
- **Tailwind CSS**: Utility-first styling

### Theme System

- **Dark/Light Mode**: Built-in theme switching with `next-themes`
- **Responsive Design**: Mobile-first approach
- **Design Tokens**: Consistent spacing, colors, and typography

### Key Components

- **Layouts**: Dashboard with sidebar, default layout
- **Forms**: React Hook Form with Zod validation
- **Tables**: TanStack Table with sorting, filtering
- **Charts**: Recharts integration for data visualization
- **Notifications**: Sonner for toast notifications

## 🔐 Authentication & Authorization

### Auth Provider

The `AuthProvider` manages:
- User session state
- JWT token handling
- Automatic token refresh
- Protected route access


## 🌐 API Integration

### Auto-Generated Client

The API client is automatically generated from the backend's OpenAPI specification:

```typescript
import { ApiClient } from '@/api'

const apiClient = new ApiClient({
  HEADERS: {
    Authorization: `Bearer ${accessToken}`
  }
})

// Type-safe API calls
const users = await apiClient.users.getUsersApiV1UsersGet()
```

### API Client Generation

When the backend API changes:

1. Ensure backend is running on `http://localhost:8000`
2. Run `pnpm run generate:api`
3. Updated TypeScript types and services are automatically generated

## 🏠 Feature Components

### Dashboard
- **Sidebar Navigation**: Role-based menu with icons
- **Responsive Layout**: Mobile-friendly sidebar collapse
- **Breadcrumb Navigation**: Context-aware navigation

### User Management
- **User List**: Paginated table with search and filters
- **User Profile**: Complete profile management with image upload
- **Role Assignment**: Assign roles to users within tenants

### Tenant Management
- **Tenant Search**: Smart search with autocomplete
- **Multi-tenancy**: Tenant-scoped data and permissions
- **Tenant Switching**: Easy switching between tenants

### AI Chat Interface
- **Real-time Streaming**: Live AI responses with typing indicators
- **Model Selection**: Choose from available AI models
- **Chat History**: Persistent conversation history
- **Mobile Optimized**: Touch-friendly chat interface

### Role & Permission Management
- **Dynamic Roles**: Create and edit roles with permissions
- **Permission Matrix**: Visual permission assignment
- **Role Hierarchy**: Support for role inheritance

## 🎨 Styling & Theming

### Tailwind CSS 4

- **Native Integration**: Direct Vite plugin support
- **Custom Configuration**: Extended theme with design tokens
- **Dark Mode**: Automatic dark/light mode switching
- **Responsive Design**: Mobile-first breakpoints

### Component Styling

```typescript
// Example component with Tailwind classes Shadcn UI https://ui.shadcn.com/docs/installation
function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }

```

## 🧪 Development Workflow

### API-First Development

1. **Backend Changes**: Update backend API endpoints
2. **Generate Client**: Run `pnpm run generate:api`
3. **Type Safety**: TypeScript ensures type safety across the stack
4. **Frontend Updates**: Use updated types and services

### Component Development

1. **shadcn/ui**: Use existing components when possible
2. **Custom Components**: Build in `components/shared/` for reusability
3. **Feature Components**: Organize by feature in `components/features/`
4. **Type Safety**: Use TypeScript interfaces for all props

### Form Handling

```typescript
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const schema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email')
})

function MyForm() {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: { name: '', email: '' }
  })
  
  const onSubmit = (data) => {
    // Type-safe form data
    console.log(data) // { name: string, email: string }
  }
  
  return <Form {...form}>...</Form>
}
```

## 📦 Build & Deployment

### Development Build

```bash
pnpm dev                    # Hot reload development server
```

### Production Build

```bash
pnpm build                  # TypeScript compilation + Vite build
pnpm preview                # Preview production build locally
```

### Build Output

- **Target Directory**: `../../backend/api/ui`
- **Optimized Assets**: Minified JavaScript, CSS, and assets
- **Static Files**: Ready for serving from any web server

## 🔧 Troubleshooting

### Common Issues

1. **API Client Generation Fails**:
   - Ensure backend is running on port 8000
   - Check backend OpenAPI endpoint: `http://localhost:8000/openapi.json`

2. **TypeScript Errors**:
   - Run `pnpm run generate:api` after backend changes
   - Clear TypeScript cache: Delete `node_modules/.cache`

3. **Styling Issues**:
   - Check Tailwind configuration
   - Verify component imports from `@/components/ui`

4. **Cloudflare DNS**:
    - Tenant contains subdomain for example:  `test.demo.fsrapp.xyz` then clouldflare doesn't provide free ssl certificate.. [Read here](https://developers.cloudflare.com/ssl/edge-certificates/)

### Development Tips

- **Hot Reload**: Vite provides instant hot module replacement
- **Type Checking**: Use `tsc --noEmit` for type checking without building
- **Debugging**: React Developer Tools and browser DevTools
- **Performance**: Use React Profiler for performance optimization

## 🤝 Contributing

1. **Follow TypeScript**: All new code should be TypeScript
2. **Use shadcn/ui**: Prefer existing components over custom ones
3. **Responsive Design**: Ensure mobile compatibility
4. **Type Safety**: Maintain end-to-end type safety
5. **API Integration**: Regenerate API client after backend changes

---

This frontend application provides a solid foundation for building modern, type-safe React applications with comprehensive UI components and seamless backend integration.