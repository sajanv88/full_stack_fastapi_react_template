import { createContext } from "react"

interface SSOConfigurationContextProps {

}

const initialState: SSOConfigurationContextProps = {}

const SSOConfigurationContext = createContext<SSOConfigurationContextProps>(initialState)



interface SSOConfigurationProviderProps {
    children: React.ReactNode;
}
export default function SSOConfigurationProvider({ children }: SSOConfigurationProviderProps) {
    return (
        <SSOConfigurationContext.Provider value={{}}>
            {children}
        </SSOConfigurationContext.Provider>
    )
}