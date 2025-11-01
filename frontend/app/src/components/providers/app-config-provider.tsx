import { AppConfigurationDto, NotificationBannerSettingDto, TenantDto } from "@/api";
import { getApiClient, setTenant } from "@/lib/utils";
import { createContext, useContext, useEffect, useState, useCallback, useMemo } from "react"
import { useAuthContext } from "./auth-provider";


export const AppConfigMessage = {
    type: "RELOAD_APP_CONFIG"
}
interface Configuration extends AppConfigurationDto {
    reloadAppConfig: () => Promise<void>;
    shouldShowTenantSelection?: boolean;
    redirectToTenantDomain: (tenant: TenantDto) => void;
    notificationBannerSetting: NotificationBannerSettingDto
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
    reloadAppConfig: async () => { },
    redirectToTenantDomain: () => { },
    environment: "development",
    notificationBannerSetting: {
        is_enabled: false,
        message: "",
    }

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
        },
        current_tenant: null,
        environment: "development"
    });
    const [shouldShowTenantSelection, setShouldShowTenantSelection] = useState(false);
    const [notificationBannerSetting, setNotificationBannerSetting] = useState<NotificationBannerSettingDto>({
        is_enabled: false,
        message: "",
    });

    const reloadAppConfig = useCallback(async function reloadAppConfig() {
        const [config, notificationSetting] = await Promise.all([
            getApiClient(accessToken).appConfiguration.getAppConfigurationApiV1AppConfigurationGet(),
            getApiClient(accessToken).notifications.getNotificationBannerApiV1NotificationsBannerGet()
        ]);
        setAppConfig(config)
        setNotificationBannerSetting(notificationSetting);
    }, [accessToken]);




    useEffect(() => {
        const fetchConfig = async () => {
            const [config, notificationSetting] = await Promise.all([
                getApiClient(accessToken).appConfiguration.getAppConfigurationApiV1AppConfigurationGet(),
                getApiClient(accessToken).notifications.getNotificationBannerApiV1NotificationsBannerGet()
            ]);
            setAppConfig(config)
            setNotificationBannerSetting(notificationSetting);
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


    }, [appConfig, accessToken, appConfig.current_tenant]);




    const redirectToTenantDomain = useCallback((tenant: TenantDto) => {
        const protocol = appConfig.environment === "development" ? "http" : "https";
        const port = appConfig.environment === "development" ? ":3000" : "";
        console.debug("Redirecting to tenant domain if needed:", tenant.custom_domain);
        const url = `${protocol}://${tenant.custom_domain || tenant.subdomain}${port}`;
        const currentHostname = window.location.hostname;
        console.debug("Current hostname:", currentHostname);
        console.debug("Target URL:", url);
        if (tenant.custom_domain) {
            if (currentHostname !== tenant.custom_domain) {
                console.debug("Redirecting to custom domain:", url);
                window.location.href = url;
                return
            }
        } else {
            if (currentHostname !== tenant.subdomain) {
                console.debug("Redirecting to subdomain:", url);

                window.location.href = url;
            }
        }

    }, [])

    const value = useMemo(() => ({
        ...appConfig,
        reloadAppConfig,
        shouldShowTenantSelection,
        redirectToTenantDomain,
        notificationBannerSetting
    }), [appConfig, notificationBannerSetting])

    return (
        <appConfigContext.Provider value={value}>
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
