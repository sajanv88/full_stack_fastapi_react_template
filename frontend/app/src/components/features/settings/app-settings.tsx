
import { useLocation } from "react-router";
import { NotificationBanner } from "@/components/features/settings/notification-banner";
import { SSOProviderConfiguration } from "@/components/features/sso-configurations/sso-provider-configuration";
import SSOConfigurationProvider from "@/components/providers/sso-configuration-provider";

export function AppSettings() {
    const { pathname } = useLocation()
    return (
        <div className="px-4 py-6 w-full xl:container xl:mx-auto xl:w-5xl">
            {pathname.includes("notifications") && <NotificationBanner />}
            {pathname.includes("sso") && (
                <SSOConfigurationProvider>
                    <SSOProviderConfiguration />
                </SSOConfigurationProvider>
            )}
        </div>
    );
}