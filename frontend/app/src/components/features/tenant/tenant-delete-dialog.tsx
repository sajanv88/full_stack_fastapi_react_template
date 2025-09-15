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

interface DeleteTenantDialogProps {
    open: boolean;
    onDismiss: () => void;
}
export function TenantDeleteDialog({ open, onDismiss }: DeleteTenantDialogProps) {
    const { selectedTenant, onDeleteTenant } = useTenants();

    function onDismissHandler(flag: boolean) {
        if (!flag) onDismiss();
    }
    return (
        <AlertDialog open={open} onOpenChange={onDismissHandler}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                    <AlertDialogDescription>
                        This action cannot be undone. This will permanently delete this
                        tenant, And all the resources that belongs to the
                        <strong className="font-bold capitalize text-red-500 px-1">{selectedTenant?.tenant?.name}</strong>
                        tenant.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={onDeleteTenant}>Continue</AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    )
}