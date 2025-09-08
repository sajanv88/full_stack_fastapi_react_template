import { AppConfigResponse } from "@/api";
import { getApiClient, setTenant } from "@/lib/utils";
import { createContext, useContext, useEffect, useState } from "react"

const appConfigContext = createContext<AppConfigResponse>({
    is_multi_tenant_enabled: false,
    multi_tenancy_strategy: "none"
});


interface AppConfigProviderProps {
    children: React.ReactNode;
}

export function AppConfigProvider({ children }: AppConfigProviderProps) {
    const [appConfig, setAppConfig] = useState<AppConfigResponse>({
        is_multi_tenant_enabled: false,
        multi_tenancy_strategy: "none"
    });

    useEffect(() => {
        const fetchConfig = async () => {
            const config = await getApiClient().appConfig.getAppConfigApiV1ConfigGet();
            setAppConfig(config)

            if (config.is_multi_tenant_enabled === false) {
                setTenant(null);
            }
        };

        fetchConfig();
    }, []);
    return (
        <appConfigContext.Provider value={appConfig}>
            {children}
        </appConfigContext.Provider>
    )
}

export function useAppConfig() {
    const context = useContext(appConfigContext);
    if (!context) {
        throw new Error("useAppConfig must be used within an AppConfigProvider");
    }
    return context;
}
