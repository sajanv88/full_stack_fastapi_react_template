import { Feature } from "@/api";
import { useAppConfig } from "@/components/providers/app-config-provider";
import { useAuthContext } from "@/components/providers/auth-provider";
import { useCallback } from "react";

export function useFeatureCheck() {
    const { current_tenant } = useAppConfig();
    const { can } = useAuthContext();
    const hostManageTenants = can("host:manage_tenants");
    const isFeatureEnabled = useCallback((feature: Feature) => {

        if (hostManageTenants) {
            return true;
        }
        if (!current_tenant && !hostManageTenants) {
            return false
        }
        if (!current_tenant?.features) {
            console.log("No features found for current tenant.");
            return false;
        }

        const onlyEnabledFeatures = current_tenant?.features?.filter(f => f.enabled).map(f => f.name) || [];
        for (const f of onlyEnabledFeatures) {
            if (f.toLowerCase() === feature.toLowerCase()) {
                return true
            }
        }
        return false;
    }, [current_tenant, hostManageTenants]);

    return { requireFeature: isFeatureEnabled };
}
