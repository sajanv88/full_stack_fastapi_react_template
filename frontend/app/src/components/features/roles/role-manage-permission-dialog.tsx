import { Permission } from "@/api";
import { useRoles } from "@/components/providers/roles-provider";
import { ListPermission } from "@/components/shared/list-permission";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogTitle } from "@/components/ui/dialog";
import { useState } from "react";
import { toast } from "sonner";

interface RoleManagePermissionDialogProps {
    open: boolean;
    onDismiss: () => void;
}

export function RoleManagePermissionDialog({ open, onDismiss }: RoleManagePermissionDialogProps) {
    const { onUpdateRole, selectedRole, refreshRoles } = useRoles()
    const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);
    function onDismissHandler(flag: boolean) {
        if (!flag) {
            onDismiss();
        }
    }
    const existingPermission = selectedRole?.role?.permissions || [];
    async function onSaveChanges() {
        try {
            const newPermissions = selectedPermissions.map(permission => permission as Permission)

            await onUpdateRole(selectedRole?.role?.id!, {
                name: selectedRole?.role?.name!,
                description: selectedRole?.role?.description!,
                permissions: newPermissions
            });
            toast.success("Role updated successfully", {
                description: "The role has been updated with the new permissions.",
                position: "top-right",
                richColors: true,
            });
            onDismiss();
            refreshRoles();
        } catch (error) {
            console.error("Error updating role:", error);
            toast.error("Failed to update role", {
                description: "There was an error updating the permissions.",
                richColors: true,
                position: "top-right"
            });
        }

    }
    return (
        <Dialog open={open} onOpenChange={onDismissHandler}>
            <DialogContent className="sm:max-w-screen-md">
                <DialogTitle>Manage Permissions</DialogTitle>
                <DialogDescription>
                    Here you can manage the permissions for this role.
                </DialogDescription>
                <section className="">
                    <ListPermission
                        multiSelect
                        value={existingPermission}
                        onChange={(permissions) => setSelectedPermissions(permissions)} />
                </section>
                <DialogFooter>
                    <Button variant="outline" onClick={onDismiss}>Cancel</Button>
                    <Button onClick={onSaveChanges} disabled={selectedPermissions.length === 0}>Save changes</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
