import { AppConfigurationDto } from "@/api";
import { getApiClient, setTenant } from "@/lib/utils";
import { createContext, useContext, useEffect, useState, useCallback } from "react"
import { useAuthContext } from "./auth-provider";

interface Configuration extends AppConfigurationDto {
    reloadAppConfig: () => Promise<void>;
    shouldShowTenantSelection?: boolean;
}
const appConfigContext = createContext<Configuration>({
    is_multi_tenant_enabled: false,
    multi_tenancy_strategy: "none",
    host_main_domain: "",
    available_ai_models: [],
    is_user_logged_in: false,
    user_preferences: {
        preferences: {},
        user_id: ""
    },
    reloadAppConfig: async () => { }
});


interface AppConfigProviderProps {
    children: React.ReactNode;
}

export function AppConfigProvider({ children }: AppConfigProviderProps) {
    const { accessToken } = useAuthContext();

    const [appConfig, setAppConfig] = useState<AppConfigurationDto>({
        is_multi_tenant_enabled: false,
        multi_tenancy_strategy: "none",
        host_main_domain: "",
        available_ai_models: [],
        is_user_logged_in: false,
        user_preferences: {
            preferences: {},
            user_id: ""
        }
    });
    const [shouldShowTenantSelection, setShouldShowTenantSelection] = useState(false);

    const reloadAppConfig = useCallback(async function reloadAppConfig() {
        if (!accessToken) return;
        const config = await getApiClient(accessToken).appConfiguration.getAppConfigurationApiV1AppConfigurationGet();
        setAppConfig(config)

    }, [accessToken]);
    useEffect(() => {

        const fetchConfig = async () => {
            const config = await getApiClient(accessToken).appConfiguration.getAppConfigurationApiV1AppConfigurationGet();
            setAppConfig(config)
            if (config.is_multi_tenant_enabled === false) {
                setTenant(null);

            }
        };
        fetchConfig();
    }, [accessToken]);

    useEffect(() => {
        if (appConfig.is_multi_tenant_enabled && !appConfig.current_tenant) {
            setShouldShowTenantSelection(true);
        }
        if (appConfig.current_tenant) {
            setTenant(appConfig.current_tenant);
        }


    }, [appConfig, accessToken]);
    return (
        <appConfigContext.Provider value={{ ...appConfig, reloadAppConfig, shouldShowTenantSelection }}>
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
