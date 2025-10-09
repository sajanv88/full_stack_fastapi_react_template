import { useAuthContext } from "@/components/providers/auth-provider";

export function TenantSetting() {
    const { can } = useAuthContext();
    const hasManageTenantSetting = can("full:access") || can("manage:storage_settings");

    if (!hasManageTenantSetting) {
        return (
            <div className="grid place-items-center place-content-center h-40">
                <p>
                    You do not have permission to view this page.
                </p>
            </div>
        );
    }

    return (
        <div>
            <h1>Tenant Settings</h1>
            <p>Manage your tenant settings here.</p>
        </div>
    );
}