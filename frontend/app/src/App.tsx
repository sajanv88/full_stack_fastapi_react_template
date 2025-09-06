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
        <Route path="profile" element={<Profile />} />
      </Route>
    </Routes>

  )
}

export default App
