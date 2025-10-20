import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Info } from "lucide-react";

export function FeatureDisabledNotice({ featureName }: { featureName: string }) {
    return (
        <section className="px-4 py-6 w-full xl:container xl:mx-auto xl:w-5xl">
            <Alert>
                <Info className="h-4 w-4" />
                <AlertTitle>{featureName} Feature Disabled</AlertTitle>
                <AlertDescription>
                    The {featureName} feature is not enabled for your tenant. Please contact your administrator for more information.
                </AlertDescription>
            </Alert>
        </section>
    )
}