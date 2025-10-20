import { Feature } from "@/api";
import { useAppConfig } from "@/components/providers/app-config-provider";
import { useAuthContext } from "@/components/providers/auth-provider";

export function useFeatureCheck() {
    const { current_tenant } = useAppConfig();
    const { can } = useAuthContext();
    const hostManageTenants = can("host:manage_tenants");
    const isFeatureEnabled = (feature: Feature) => {
        if (hostManageTenants) {
            return true;
        }
        if (!current_tenant && !hostManageTenants) {
            return false
        }

        for (const f of current_tenant?.features || []) {
            if (f.name === feature && f.enabled) {
                return true
            }
            break
        }
        return false;
    };

    return { requireFeature: isFeatureEnabled };
}
