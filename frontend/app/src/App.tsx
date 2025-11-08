import { Routes, Route, Navigate } from "react-router";
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
import { useAuthContext } from "./components/providers/auth-provider";
import { AIChatProvider } from "@/components/providers/ai-chat-provider";
import { PasswordResetRequest } from "@/components/features/auth/password-reset-request";
import { PasswordResetConfirmation } from "@/components/features/auth/password_reset_confirmation";
import { Activation } from "@/components/features/auth/activation";
import { TenantSetting } from "@/components/features/tenant/tenant-setting";
import { MagicLinkLoginValidate } from "@/components/features/auth/magic-link-login-validate";
import { NonActiveTenantView } from "@/components/shared/non-active-tenant-view";
import { StripeProvider } from "@/components/providers/stripe-provider";
import { ConfigureStripe } from "@/components/features/billings/stripe/configure-stripe";
import { BillingOverview } from "@/components/features/billings/stripe/billing-overview";
import { Billing } from "@/components/features/billings/stripe/billing";
import { Invoices } from "@/components/features/billings/stripe/invoices";
import { Products } from "@/components/features/billings/stripe/products";
import { CheckoutOverview } from "@/components/features/billings/stripe/checkout-overview";
import { AppSettings } from "@/components/features/settings/app-settings";
import { AuditLogProvider } from "@/components/providers/audit-log-provider";
import { AuditLogs } from "@/components/features/audit-logs/audit-logs";

function App() {
  const { user } = useAuthContext();
  return (
    <Routes>
      <Route element={<DefaultLayout />}>
        <Route index path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="forgot-password" element={<PasswordResetRequest />} />
        <Route path="password_reset_confirmation" element={<PasswordResetConfirmation />} />
        <Route path="activation" element={<Activation />} />
        <Route path="magic_link_login" element={<MagicLinkLoginValidate />} />
        <Route path="non-active" element={<NonActiveTenantView />} />
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
        {!user?.tenant_id && (
          <Route path="tenants" element={
            <TenantsProvider>
              <Tenants />
            </TenantsProvider>
          }
          />
        )}
        <Route path="audit-logs" element={
          <AuditLogProvider>
            <AuditLogs />
          </AuditLogProvider>
        }
        />

        <Route path="settings" element={
          <SettingsProvider>
            <Settings />
          </SettingsProvider>
        } />

        <Route path="settings/general" element={
          <SettingsProvider>
            <TenantsProvider>
              <TenantSetting />
            </TenantsProvider>
          </SettingsProvider>
        } />

        <Route path="settings/payment" element={
          <StripeProvider>
            <ConfigureStripe />
          </StripeProvider>
        } />

        <Route path="settings/notifications" element={
          <AppSettings />
        } />

        <Route path="billing" element={<Billing />}>
          <Route index element={<BillingOverview />} />
          <Route path="invoices" element={<Invoices />} />
          <Route path="products" element={<Products />} />
          <Route path="checkouts" element={<CheckoutOverview />} />
        </Route>

        <Route path="profile" element={<Profile />} />
        <Route path="ai" element={
          <AIChatProvider>
            <AIChat />
          </AIChatProvider>
        } />

        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Route>
    </Routes>

  )
}

export default App
