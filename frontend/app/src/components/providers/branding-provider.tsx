import { createContext, useContext, useState, useEffect } from "react";
import { toast } from "sonner";
import { BrandingDto, UpdateBrandingDto } from "@/api";
import { useAuthContext } from "@/components/providers/auth-provider";
import { getApiClient } from "@/lib/utils";
import { useAppConfig } from "@/components/providers/app-config-provider";

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
    const { branding: initialBranding, reloadAppConfig } = useAppConfig();
    const [branding, setBranding] = useState<BrandingDto | undefined>(undefined);
    const { accessToken } = useAuthContext();


    async function onUpdateBranding(data: UpdateBrandingDto) {
        try {
            const apiClient = getApiClient(accessToken);
            await apiClient.brandings.updateBrandingApiV1BrandingsPost({
                requestBody: data
            });
            toast.success("Branding updated successfully", { richColors: true, position: "top-right" });
            await reloadAppConfig();
        } catch (error) {
            console.error("Failed to update branding", error);
            toast.error("Failed to update branding", { richColors: true, position: "top-right" });
        }
    }

    useEffect(() => {
        if (initialBranding) {
            setBranding(initialBranding);
        }
    }, [initialBranding]);


    return (
        <BrandingContext.Provider value={{ branding, onUpdateBranding }}>
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