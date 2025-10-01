import { useEffect, useState } from "react";
import { useDebounce } from "./use-debounce";
import { getApiClient } from "@/lib/utils";
import { useAppConfig } from "@/components/providers/app-config-provider";
import { ApiError, TenantDto } from "@/api";

export function useSubdomainCheck() {
    const { host_main_domain } = useAppConfig();
    const [subdomain, setSubdomain] = useState("");
    const debouncedText = useDebounce(subdomain, 800); // 800ms debounce
    const [tenantDetails, setTenantDetails] = useState<TenantDto | null>(null);
    const [isChecking, setIsChecking] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function checkSubdomainAvailability() {
        const apiClient = getApiClient();
        try {
            setIsChecking(true);
            const response = await apiClient.tenants.searchBySubdomainApiV1TenantsSearchBySubdomainSubdomainGet({
                subdomain: `${debouncedText}.${host_main_domain}`
            });
            setTenantDetails(response);
            setError(null);
        } catch (error) {
            console.error("Error checking subdomain availability:", error);
            if (error instanceof ApiError) {
                setError(error.body?.detail || "Failed to check subdomain availability. Please try again.");
            } else {
                setError("Failed to check subdomain availability. Please try again.");
            }
            setTenantDetails(null);
        } finally {
            setIsChecking(false);
        }
    }
    useEffect(() => {
        if (debouncedText) {
            checkSubdomainAvailability();
        } else {
            setTenantDetails(null);
            setError(null);
        }
    }, [debouncedText]);

    return { setSubdomain, tenantDetails, isChecking, error };


}