import { Routes, Route } from "react-router";
import { DefaultLayout } from "@/components/layouts/default-layout";
import { Login } from "@/components/features/auth/login";
import { Dashboard } from "@/components/features/dashboard/dashboard";
import { DashboardLayout } from "@/components/layouts/dashboard-layout";
import { Profile } from "@/components/features/profile/profile";
import { Roles } from "@/components/features/roles/roles";
import { Users } from "@/components/features/users/users";
import Register from "@/components/features/auth/register";
import { UsersProvider } from "@/components/providers/users-provider";
import { RolesProvider } from "@/components/providers/roles-provider";
import { AIChat } from "@/components/features/ai-chat/ai-chat";
import { TenantsProvider } from "@/components/providers/tenant-provider";
import { Tenants } from "@/components/features/tenant/tenant";
import { SettingsProvider } from "@/components/providers/settings-provider";
import { Settings } from "@/components/features/settings/settings";

function App() {

  return (
    <Routes>
      <Route element={<DefaultLayout />}>
        <Route index path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
      </Route>

      <Route element={<DashboardLayout />}>
        <Route index path="dashboard" element={<Dashboard />} />
        <Route path="users" element={
          <UsersProvider>
            <Users />
          </UsersProvider>
        }
        />
        <Route path="roles" element={
          <RolesProvider>
            <Roles />
          </RolesProvider>
        }
        />
        <Route path="tenants" element={
          <TenantsProvider>
            <Tenants />
          </TenantsProvider>
        }
        />

        <Route path="settings" element={
          <SettingsProvider>
            <Settings />
          </SettingsProvider>
        }
        />

        <Route path="profile" element={<Profile />} />
        <Route path="ai" element={<AIChat />} />
      </Route>
    </Routes>

  )
}

export default App
