import { StorageSettings } from "@/api";
import { getApiClient } from "@/lib/utils";
import { useContext, createContext, useEffect, useState } from "react";
import { toast } from "sonner";

interface SettingsContextProps {
    storages: StorageSettings[]
    availableStorages: Array<Record<string, string>>
    onConfigureStorage: (settings: StorageSettings) => Promise<void>;
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
    const apiClient = getApiClient();
    const [storages, setStorages] = useState<StorageSettings[]>([]);
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

    async function onConfigureStorage(settings: StorageSettings) {
        await apiClient.storageSettings.configureStorageApiV1StorageConfigurePost({
            requestBody: settings
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