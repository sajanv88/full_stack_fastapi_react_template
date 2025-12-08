import { BrandingDto, UpdateBrandingDto } from "@/api";
import { createContext, useContext } from "react";

interface BrandingProviderState {
    branding?: BrandingDto
    onUpdateBranding: (data: UpdateBrandingDto) => Promise<void>;
}

const initialState: BrandingProviderState = {
    onUpdateBranding: async () => { },
}

const BrandingContext = createContext<BrandingProviderState>(initialState);
interface BrandingProviderProps {
    children: React.ReactNode;
}

export function BrandingProvider({ children }: BrandingProviderProps) {
    // const [branding, setBranding] = useState<BrandingDto | undefined>(undefined);
    return (
        <BrandingContext.Provider value={initialState}>
            {children}
        </BrandingContext.Provider>
    )
}

export function useBrandingContext() {
    const ctx = useContext(BrandingContext);
    if (!ctx) {
        throw new Error("useBrandingContext must be used within a BrandingProvider");
    }
    return ctx;
}