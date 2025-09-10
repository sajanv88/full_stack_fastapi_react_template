import { useContext, createContext } from "react";

interface SettingsContextProps {
    name: string
}

const initialState: SettingsContextProps = {
    name: "Default Name"
};

const SettingsContext = createContext<SettingsContextProps>(initialState);

interface SettingsProviderProps {
    children: React.ReactNode;
}
export function SettingsProvider({ children }: SettingsProviderProps) {
    return (
        <SettingsContext.Provider value={initialState}>
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