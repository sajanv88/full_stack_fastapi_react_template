import { useAuthContext } from "@/components/providers/auth-provider";
import { useTenants } from "@/components/providers/tenant-provider";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { getApiClient } from "@/lib/utils";
import { toast } from "sonner";

interface ManageTenantSubscriptionProps {
    open: boolean;
    onDismiss: () => void;
}
export function ManageTenantSubscription({ open, onDismiss }: ManageTenantSubscriptionProps) {
    const { selectedTenant, onSelectTenant, refreshTenants } = useTenants();
    const { accessToken } = useAuthContext();
    function onDismissHandler(flag: boolean) {
        if (!flag) onDismiss();
    }

    async function enableTrialPlan() {
        if (!selectedTenant) return;
        try {
            const apiClient = getApiClient(accessToken).tenants
            await apiClient.activateTrialPlanApiV1TenantsTenantIdActivateTrialPlanPatch({
                tenantId: selectedTenant.tenant.id!
            })
            toast.success("Trial plan activated successfully for tenant.", {
                richColors: true,
                position: "top-right"
            });
            refreshTenants();
            onSelectTenant()
        }
        catch (error) {
            toast.error("Failed to activate trial plan for tenant.", {
                richColors: true,
                position: "top-right"
            });
        }

    }
    const current_subscription = selectedTenant?.tenant?.subscription_id;

    return (
        <AlertDialog open={open} onOpenChange={onDismissHandler}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Manage Tenant Subscription</AlertDialogTitle>
                    <AlertDialogDescription>
                        By managing the subscription, you can upgrade, downgrade, or cancel the subscription plan for the
                        <strong className="font-bold capitalize text-red-500 px-1">{selectedTenant?.tenant?.name}</strong>
                        tenant.
                        {current_subscription ? (
                            <p className="mt-2">Current Subscription ID: <strong>{current_subscription}</strong></p>
                        ) : (
                            <p className="mt-2 font-bold">
                                Do you want to enable a trial subscription for this tenant? <br />
                            </p>
                        )}
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    {!current_subscription && (
                        <>
                            <AlertDialogCancel>No</AlertDialogCancel>
                            <AlertDialogAction onClick={enableTrialPlan}>Yes</AlertDialogAction>
                        </>
                    )}
                    {current_subscription && (
                        <>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction >Confirm</AlertDialogAction>
                        </>
                    )}

                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    )
}