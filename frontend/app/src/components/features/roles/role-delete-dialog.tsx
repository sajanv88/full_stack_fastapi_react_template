import { useRoles } from "@/components/providers/roles-provider";
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

interface DeleteNewRoleDialogProps {
    open: boolean;
    onDismiss: () => void;
}
export function RoleDeleteDialog({ open, onDismiss }: DeleteNewRoleDialogProps) {
    const { selectedRole, onDeleteRole } = useRoles();
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
                        role <strong className="font-bold text-red-500">{selectedRole?.role?.name}</strong>.
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={onDeleteRole}>Continue</AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    )
}