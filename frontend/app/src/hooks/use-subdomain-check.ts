import { useEffect, useState } from "react";
import { useDebounce } from "./use-debounce";
import { getApiClient } from "@/lib/utils";
import { useAppConfig } from "@/components/providers/app-config-provider";
import { ApiError } from "@/api";

export function useSubdomainCheck() {
    const { host_main_domain } = useAppConfig();
    const [subdomain, setSubdomain] = useState("");
    const debouncedText = useDebounce(subdomain, 800); // 800ms debounce
    const [isAvailable, setIsAvailable] = useState<boolean | null>(null);
    const [isChecking, setIsChecking] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function checkSubdomainAvailability() {
        const apiClient = getApiClient();
        try {
            setIsChecking(true);
            const response = await apiClient.tenants.checkTenantBySubdomainApiV1TenantsCheckSubdomainSubdomainGet({
                subdomain: `${debouncedText}.${host_main_domain}`
            });
            setIsAvailable(response.available);
            setError(null);
        } catch (error) {
            console.error("Error checking subdomain availability:", error);
            if (error instanceof ApiError) {
                setError(error.body?.detail || "Failed to check subdomain availability. Please try again.");
            } else {
                setError("Failed to check subdomain availability. Please try again.");
            }
            setIsAvailable(null);
        } finally {
            setIsChecking(false);
        }
    }
    useEffect(() => {
        if (debouncedText) {
            checkSubdomainAvailability();
        } else {
            setIsAvailable(null);
            setError(null);
        }
    }, [debouncedText]);

    return { setSubdomain, isAvailable, isChecking, error };


}