import { Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";

interface BannerProps {
    isEnabled: boolean;
    message?: string | null;
}
export function Banner({ isEnabled, message }: BannerProps) {
    if (!isEnabled) return null;

    return (
        <section className="mx-5 mb-3 mt-3">
            <Alert variant="info" >
                <Info className="h-4 w-4 mr-2" />
                <AlertTitle>Information</AlertTitle>
                <AlertDescription>{message}</AlertDescription>
            </Alert>
        </section>
    );
}