import { CreateSSOSettingsDto, SSOSettingsListDto, UpdateSSOSettingsDto } from "@/api";
import { createContext, useContext, useState, useEffect } from "react"
import { useAuthContext } from "./auth-provider";
import { getApiClient } from "@/lib/utils";
import { toast } from "sonner";
import { NoPermissionToAccessResource } from "../shared/no-permission-access-resource";

type ProviderType = SSOSettingsListDto["items"]
interface SSOConfigurationContextProps {
    onRefreshSSOConfigurations: () => Promise<void>;
    providers: ProviderType;
    availableProviders: string[];
    onCreateSSOConfiguration: (params: CreateSSOSettingsDto) => Promise<void>;
    onEnableOrDisableSSOLogin: (ssoId: string, enabled: boolean) => Promise<void>;
    onDeleteSSOConfiguration: (ssoId: string) => Promise<void>;
    onUpdateSSOConfiguration: (ssoId: string, params: UpdateSSOSettingsDto) => Promise<void>;
}

const initialState: SSOConfigurationContextProps = {
    onRefreshSSOConfigurations: async () => { },
    providers: [],
    availableProviders: [],
    onCreateSSOConfiguration: async () => { },
    onEnableOrDisableSSOLogin: async () => { },
    onDeleteSSOConfiguration: async () => { },
    onUpdateSSOConfiguration: async () => { },
}

const SSOConfigurationContext = createContext<SSOConfigurationContextProps>(initialState)



interface SSOConfigurationProviderProps {
    children: React.ReactNode;
}
export default function SSOConfigurationProvider({ children }: SSOConfigurationProviderProps) {
    const [providers, setProviders] = useState<ProviderType>([])
    const { accessToken, can } = useAuthContext();
    const [availableProviders, setAvailableProviders] = useState<string[]>([]);
    const canManageSSOSettings = can('full:access');

    async function fetchAllSSOProviders() {
        try {
            const apiClient = getApiClient(accessToken);
            const [availableProvidersResponse, ssoProvidersResponse] = await Promise.all([
                apiClient.ssoSettings.getAvailableSsoProvidersApiV1SsosAvailableProvidersGet(),
                apiClient.ssoSettings.listApiV1SsosGet()
            ]);
            setAvailableProviders(availableProvidersResponse);
            setProviders(ssoProvidersResponse.items);
            // const filteredProviders = availableProvidersResponse.map(item => ssoProvidersResponse.items.filter(sso => sso.provider !== item));
            // setAvailableProviders(filteredProviders);
        } catch (error) {
            console.error("Failed to fetch SSO providers:", error);
            toast.error("Failed to fetch SSO providers", { richColors: true, position: "top-right" });
        }
    }
    async function refreshSSOConfigurations() {
        await fetchAllSSOProviders();
    }
    async function createSSOConfiguration(params: CreateSSOSettingsDto) {
        try {
            const apiClient = getApiClient(accessToken);
            await apiClient.ssoSettings.createSsoSettingsApiV1SsosPost({
                requestBody: params
            });
            toast.success("SSO configuration created successfully", { richColors: true, position: "top-right" });
            await fetchAllSSOProviders();
        } catch (error) {
            console.error("Failed to create SSO configuration:", error);
            toast.error("Failed to create SSO configuration", { richColors: true, position: "top-right" });
        }
    }

    async function enableOrDisableSSOLogin(ssoId: string, enabled: boolean) {
        try {
            const apiClient = getApiClient(accessToken);
            const existing = providers.find(p => p.id === ssoId);
            if (!existing) {
                toast.error("SSO configuration not found", { richColors: true, position: "top-right" });
                return;
            }
            await apiClient.ssoSettings.updateSsoSettingsApiV1SsosSsoIdPatch({
                ssoId,
                requestBody: { ...existing, enabled }
            });
            toast.success(`SSO configuration ${enabled ? "enabled" : "disabled"} successfully`, { richColors: true, position: "top-right" });
            await fetchAllSSOProviders();
        } catch (error) {
            console.error("Failed to toggle SSO configuration:", error);
            toast.error("Failed to toggle SSO configuration", { richColors: true, position: "top-right" });
        }
    }

    async function deleteSSOConfiguration(ssoId: string) {
        try {
            const apiClient = getApiClient(accessToken);
            await apiClient.ssoSettings.deleteSsoSettingsApiV1SsosSsoIdDelete({
                ssoId
            });
            toast.success("SSO configuration deleted successfully", { richColors: true, position: "top-right" });
            await fetchAllSSOProviders();
        } catch (error) {
            console.error("Failed to delete SSO configuration:", error);
            toast.error("Failed to delete SSO configuration", { richColors: true, position: "top-right" });
        }
    }

    async function updateSSOConfiguration(ssoId: string, params: UpdateSSOSettingsDto) {
        try {
            const apiClient = getApiClient(accessToken);
            await apiClient.ssoSettings.updateSsoSettingsApiV1SsosSsoIdPatch({
                ssoId,
                requestBody: params
            });
            toast.success("SSO configuration updated successfully", { richColors: true, position: "top-right" });
            await fetchAllSSOProviders();
        } catch (error) {
            console.error("Failed to update SSO configuration:", error);
            toast.error("Failed to update SSO configuration", { richColors: true, position: "top-right" });
        }
    }

    useEffect(() => {
        if (accessToken && canManageSSOSettings) {
            fetchAllSSOProviders();
        }
    }, [accessToken, canManageSSOSettings])

    if (!canManageSSOSettings) {
        return <NoPermissionToAccessResource message='SSO Settings' />;
    }
    return (
        <SSOConfigurationContext.Provider
            value={{
                onRefreshSSOConfigurations: refreshSSOConfigurations,
                providers,
                availableProviders,
                onCreateSSOConfiguration: createSSOConfiguration,
                onEnableOrDisableSSOLogin: enableOrDisableSSOLogin,
                onDeleteSSOConfiguration: deleteSSOConfiguration,
                onUpdateSSOConfiguration: updateSSOConfiguration,
            }}>
            {children}
        </SSOConfigurationContext.Provider>
    )
}

export function useSSOConfiguration() {
    const ctx = useContext(SSOConfigurationContext)
    if (!ctx) {
        throw new Error("useSSOConfiguration must be used within a SSOConfigurationProvider")
    }
    return ctx
}