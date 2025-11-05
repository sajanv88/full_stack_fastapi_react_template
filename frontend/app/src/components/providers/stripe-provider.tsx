import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { CreateStripeSettingDto, StripeSettingDto } from "@/api"
import { useAuthContext } from "./auth-provider";
import { getApiClient } from "@/lib/utils";
import { toast } from "sonner";
import { FeatureDisabledNotice } from "@/components/shared/feature-disabled";
import { useFeatureCheck } from "@/hooks/use-feature-check";
import { useAppConfig } from "@/components/providers/app-config-provider";
import { NoPermissionToAccessResource } from "@/components/shared/no-permission-access-resource";


interface StripeProviderState {
    onConfigureStripe: (data: CreateStripeSettingDto) => Promise<void>;
    configuredStripeSetting: StripeSettingDto | null;
    loading: boolean;
    onRefreshStripeSetting: () => Promise<void>;
    showConfigureStripe: boolean;
    stripeConfigurationError: boolean;
}

const initialStripeProviderState: StripeProviderState = {
    onConfigureStripe: async () => { },
    configuredStripeSetting: null,
    loading: true,
    onRefreshStripeSetting: async () => { },
    showConfigureStripe: false,
    stripeConfigurationError: false,
}

const StripeContext = createContext<StripeProviderState>(initialStripeProviderState);

interface StripeProviderProps {
    children: React.ReactNode;
}

export function StripeProvider({ children }: StripeProviderProps) {
    const { accessToken, can } = useAuthContext();
    const { current_tenant } = useAppConfig();
    const [configuredStripeSetting, setConfiguredStripeSetting] = useState<StripeSettingDto | null>(null);
    const [loading, setLoading] = useState(true);
    const [showConfigureStripe, setShowConfigureStripe] = useState(false);
    const featureCheck = useFeatureCheck();
    const [stripeConfigurationError, setStripeConfigurationError] = useState<boolean>(false);
    const canManageBilling = can("manage:billing") || can("full:access");

    const isStripePaymentsFeatureEnabled = featureCheck.requireFeature("stripe");

    async function fetchConfiguredStripeSetting() {
        try {
            const setting = await getApiClient(accessToken).stripe.getStripeSettingsApiV1ConfigurationsStripeGet();
            setConfiguredStripeSetting(setting);
        } catch (error) {
            console.error("Error fetching configured Stripe setting:", error);
            setShowConfigureStripe(true);
            setStripeConfigurationError(true);
        } finally {
            setLoading(false);
        }
    }


    useEffect(() => {
        if (accessToken && isStripePaymentsFeatureEnabled && current_tenant && canManageBilling) {
            fetchConfiguredStripeSetting();
        }
    }, [accessToken, isStripePaymentsFeatureEnabled, canManageBilling, current_tenant]);

    useEffect(() => {
        if (!current_tenant) {
            setLoading(false);
        }
    }, [current_tenant])


    const onConfigureStripe = useCallback(async (data: CreateStripeSettingDto) => {
        if (!accessToken || !isStripePaymentsFeatureEnabled || !canManageBilling) return;
        try {
            setLoading(true);
            await getApiClient(accessToken).stripe.configureStripeSettingApiV1ConfigurationsStripePost({
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
    }, [accessToken, isStripePaymentsFeatureEnabled, canManageBilling]);


    const onRefreshStripeSetting = useCallback(async () => {
        if (!accessToken || !isStripePaymentsFeatureEnabled || !canManageBilling) return;
        await fetchConfiguredStripeSetting();
    }, [accessToken, isStripePaymentsFeatureEnabled, canManageBilling]);


    if (!isStripePaymentsFeatureEnabled) {
        return <FeatureDisabledNotice featureName="Stripe Payments" />;
    }

    if (!canManageBilling) {
        return <NoPermissionToAccessResource message='Billing Management' />;
    }

    return (
        <StripeContext.Provider value={{
            onConfigureStripe,
            configuredStripeSetting,
            loading,
            onRefreshStripeSetting,
            showConfigureStripe,
            stripeConfigurationError
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