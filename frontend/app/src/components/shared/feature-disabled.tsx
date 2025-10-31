import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Info } from "lucide-react";
import { useAppConfig } from "../providers/app-config-provider";

export function FeatureDisabledNotice({ featureName }: { featureName: string }) {
    const { current_tenant } = useAppConfig();
    return (
        <section className="px-4 py-6 w-full xl:container xl:mx-auto xl:w-5xl">
            <Alert>
                <Info className="h-4 w-4" />
                <AlertTitle>{featureName} Feature Disabled</AlertTitle>
                <AlertDescription>
                    <p>
                        The {featureName} feature is not enabled for <strong className="capitalize inline">{current_tenant?.name}</strong>. Please contact your Host for more information.
                    </p>
                </AlertDescription>
            </Alert>
        </section>
    )
}