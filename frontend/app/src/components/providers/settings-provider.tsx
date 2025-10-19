import { AvailableStorageProviderDto, StorageSettingsDto } from "@/api";
import { getApiClient } from "@/lib/utils";
import { useContext, createContext, useEffect, useState } from "react";
import { toast } from "sonner";
import { useAuthContext } from "./auth-provider";

export interface StorageFormData extends Omit<AvailableStorageProviderDto, 'id' | 'created_at' | 'updated_at'> { }
interface SettingsContextProps {
    storages: AvailableStorageProviderDto[]
    availableStorages: Array<Record<string, string>>
    onConfigureStorage: (settings: StorageFormData) => Promise<void>;
    loading: boolean;
}


const initialState: SettingsContextProps = {
    storages: [],
    availableStorages: [],
    onConfigureStorage: async () => { },
    loading: true
};

const SettingsContext = createContext<SettingsContextProps>(initialState);

interface SettingsProviderProps {
    children: React.ReactNode;
}
export function SettingsProvider({ children }: SettingsProviderProps) {
    const { accessToken } = useAuthContext();
    const apiClient = getApiClient(accessToken);
    const [storages, setStorages] = useState<AvailableStorageProviderDto[]>([]);
    const [availableStorages, setAvailableStorages] = useState<Array<Record<string, string>>>([]);
    const [loading, setLoading] = useState(true);

    async function fetchSettings() {
        setLoading(true);
        const [storages, availables] = await Promise.all([
            apiClient.storageSettings.getStorageSettingsApiV1StorageGet(),
            apiClient.storageSettings.getAvailableProvidersApiV1StorageAvailableGet()
        ]);
        setStorages(storages);
        setAvailableStorages(availables);
        setLoading(false);
    }

    async function onConfigureStorage(settings: StorageFormData) {
        try {
            const update = { ...storages.find(s => s.provider === settings.provider), ...settings };
            const requestPayload: StorageSettingsDto = {
                provider: update.provider,
                aws_access_key: update.aws_access_key,
                aws_secret_key: update.aws_secret_key,
                region: update.region,
                aws_bucket_name: update.aws_bucket_name,
                azure_connection_string: update.azure_connection_string,
                azure_container_name: update.azure_container_name,
                is_enabled: update.is_enabled,
            }
            await apiClient.storageSettings.configureStorageApiV1StorageConfigurePost({
                requestBody: requestPayload
            });
            const updatedStorages = await apiClient.storageSettings.getStorageSettingsApiV1StorageGet();
            setStorages(updatedStorages);
            toast.success("Storage settings updated successfully", {
                richColors: true,
                position: "top-right",
            });
            await fetchSettings();
        } catch (error) {
            toast.error("Failed to update storage settings", {
                description: (error as Error).message,
                richColors: true,
                position: "top-right",
            });
        }

    }

    useEffect(() => {
        fetchSettings();
    }, [accessToken])

    return (
        <SettingsContext.Provider value={{ loading, onConfigureStorage, storages, availableStorages }}>
            {children}
        </SettingsContext.Provider>
    );
}

export function useSettings() {
    const context = useContext(SettingsContext);
    if (!context) {
        throw new Error("useSettings must be used within a SettingsProvider");
    }
    return context;
}