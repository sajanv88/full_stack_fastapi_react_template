import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { CreateStripeSettingDto, StripeSettingDto } from "@/api"
import { useAuthContext } from "./auth-provider";
import { getApiClient } from "@/lib/utils";
import { toast } from "sonner";
import { FeatureDisabledNotice } from "../shared/feature-disabled";
import { useFeatureCheck } from "@/hooks/use-feature-check";


interface StripeProviderState {
    onConfigureStripe: (data: CreateStripeSettingDto) => Promise<void>;
    configuredStripeSetting: StripeSettingDto | null;
    loading: boolean;
    onRefreshStripeSetting: () => Promise<void>;
    showConfigureStripe: boolean;
}

const initialStripeProviderState: StripeProviderState = {
    onConfigureStripe: async () => { },
    configuredStripeSetting: null,
    loading: true,
    onRefreshStripeSetting: async () => { },
    showConfigureStripe: false,
}

const StripeContext = createContext<StripeProviderState>(initialStripeProviderState);

interface StripeProviderProps {
    children: React.ReactNode;
}

export function StripeProvider({ children }: StripeProviderProps) {
    const { accessToken } = useAuthContext();
    const [configuredStripeSetting, setConfiguredStripeSetting] = useState<StripeSettingDto | null>(null);
    const [loading, setLoading] = useState(true);
    const [showConfigureStripe, setShowConfigureStripe] = useState(false);
    const featureCheck = useFeatureCheck();


    const isStripePaymentsFeatureEnabled = featureCheck.requireFeature("stripe");
    console.log("Is Stripe Payments Feature Enabled:", isStripePaymentsFeatureEnabled);
    async function fetchConfiguredStripeSetting() {
        try {
            const setting = await getApiClient(accessToken).stripe.getStripeSettingsApiV1StripeGet();
            setConfiguredStripeSetting(setting);
        } catch (error) {
            console.error("Error fetching configured Stripe setting:", error);
            setShowConfigureStripe(true);
        } finally {
            setLoading(false);
        }
    }


    useEffect(() => {
        if (accessToken && isStripePaymentsFeatureEnabled) {
            fetchConfiguredStripeSetting();
        }
    }, [accessToken, isStripePaymentsFeatureEnabled]);

    const onConfigureStripe = useCallback(async (data: CreateStripeSettingDto) => {
        if (!accessToken || !isStripePaymentsFeatureEnabled) return;
        try {
            setLoading(true);
            await getApiClient(accessToken).stripe.configureStripeSettingApiV1StripeConfigurePost({
                requestBody: data
            });
            await fetchConfiguredStripeSetting();
            toast.success("Stripe setting configured successfully.", { richColors: true, position: "top-right" });
        } catch (error) {
            console.error("Error configuring Stripe setting:", error);
            toast.error("Failed to configure Stripe setting.", { richColors: true, position: "top-right" });
        } finally {
            setLoading(false);
        }
    }, [accessToken, isStripePaymentsFeatureEnabled]);

    const onRefreshStripeSetting = useCallback(async () => {
        await fetchConfiguredStripeSetting();
    }, [accessToken, isStripePaymentsFeatureEnabled]);


    if (!isStripePaymentsFeatureEnabled) {
        return <FeatureDisabledNotice featureName="Stripe Payments" />;
    }
    return (
        <StripeContext.Provider value={{
            onConfigureStripe,
            configuredStripeSetting,
            loading,
            onRefreshStripeSetting,
            showConfigureStripe
        }}>
            {children}
        </StripeContext.Provider>
    )
}

export function useStripeProvider() {
    const context = useContext(StripeContext);
    if (!context) {
        throw new Error("useStripeProvider must be used within a StripeProvider");
    }
    return context;
}