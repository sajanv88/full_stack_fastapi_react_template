import { Alert, AlertDescription } from "@/components/ui/alert";
import { NavLink } from "react-router";
import { IconReceiptEuro } from "@tabler/icons-react"

export function ConfigureStripeNow() {
    return (
        <Alert variant="destructive">
            <IconReceiptEuro className="h-4 w-4" />
            <AlertDescription >
                <p>
                    Please configure Stripe settings to view billing information.
                    <NavLink to="/settings/payment" className="text-primary underline hover:text-primary/80 ml-1">
                        Configure Now
                    </NavLink>
                </p>
            </AlertDescription>
        </Alert>
    )
}