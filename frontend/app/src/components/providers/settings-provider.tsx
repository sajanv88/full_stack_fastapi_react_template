import { AvailableStorageProviderDTO } from "@/api";
import { getApiClient } from "@/lib/utils";
import { useContext, createContext, useEffect, useState } from "react";
import { toast } from "sonner";
import { useAuthContext } from "./auth-provider";

export interface StorageFormData extends Omit<AvailableStorageProviderDTO, 'id' | 'created_at' | 'updated_at'> { }
interface SettingsContextProps {
    storages: AvailableStorageProviderDTO[]
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
    const [storages, setStorages] = useState<AvailableStorageProviderDTO[]>([]);
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
        const update = { ...storages.find(s => s.provider === settings.provider), ...settings } as AvailableStorageProviderDTO;
        await apiClient.storageSettings.configureStorageApiV1StorageConfigurePost({
            requestBody: update
        });
        const updatedStorages = await apiClient.storageSettings.getStorageSettingsApiV1StorageGet();
        setStorages(updatedStorages);
        toast.success("Storage settings updated successfully", {
            richColors: true,
            position: "top-center",
        });
        await fetchSettings();
    }

    useEffect(() => {
        fetchSettings();
    }, [])

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