
import { useLocation } from "react-router";
import { NotificationBanner } from "@/components/features/settings/notification-banner";
import { SSOProviderConfiguration } from "@/components/features/settings/sso-provider-configuration";

export function AppSettings() {
    const { pathname } = useLocation()
    return (
        <div className="w-full xl:container xl:mx-auto xl:max-w-4xl space-y-6">
            {pathname.includes("notifications") && <NotificationBanner />}
            {pathname.includes("sso") && <SSOProviderConfiguration />}
        </div>
    );
}