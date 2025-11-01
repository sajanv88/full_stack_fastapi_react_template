
import { NotificationBanner } from "./notification-banner";

export function AppSettings() {
    return (
        <div className="w-full xl:container xl:mx-auto xl:max-w-4xl space-y-6">
            {/* Notification Banner Settings */}
            <NotificationBanner />

            {/* Future settings sections will be added here */}
        </div>
    );
}