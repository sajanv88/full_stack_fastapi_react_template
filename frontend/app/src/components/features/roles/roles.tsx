import { useRoles } from "@/components/providers/roles-provider";
import { PageHeader } from "@/components/shared/page-header";
import { useState } from "react";
import { RoleTable } from "@/components/features/roles/role-table";
import { CreateNewRoleDialog } from "@/components/features/roles/create-new-role-dialog";
import { RoleDeleteDialog } from "@/components/features/roles/role-delete-dialog";
import { RoleEditDialog } from "@/components/features/roles/role-edit-dialog";
import { RoleManagePermissionDialog } from "@/components/features/roles/role-manage-permission-dialog";
import { useAuthContext } from "@/components/providers/auth-provider";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { InfoIcon } from 'lucide-react'

export function Roles() {
    const { roleResponse, refreshRoles, selectedRole, onSelectRole, loading, error } = useRoles();
    const [isCreateNewRoleDialogOpen, setIsCreateNewRoleDialogOpen] = useState(false);
    const { can } = useAuthContext();
    const isAdmin = can("full:access");
    const isRoleManager = can("role:read_and_write_only");

    const disableCreateNewRoleBtn = !isAdmin && !isRoleManager;
    const onCreateNewRoleDismissHandler = () => {
        refreshRoles();
        setIsCreateNewRoleDialogOpen(false);
    }

    const onRoleEditDismissHandler = () => {
        onSelectRole();
        refreshRoles();
    }
    return (
        <section className="w-full 2xl:container 2xl:mx-auto ">
            <PageHeader title="Roles" subtitle="Manage your roles"
                cta={{
                    label: "Add Role",
                    onClick: () => setIsCreateNewRoleDialogOpen(true),
                    disabled: disableCreateNewRoleBtn
                }}
            />
            <CreateNewRoleDialog open={isCreateNewRoleDialogOpen} onDismiss={onCreateNewRoleDismissHandler} />
            {selectedRole?.type === 'manage_permissions' && <RoleManagePermissionDialog open={true} onDismiss={onRoleEditDismissHandler} />}
            {selectedRole?.type === 'edit' && <RoleEditDialog open={true} onDismiss={onRoleEditDismissHandler} />}
            {selectedRole?.type === 'delete' && <RoleDeleteDialog open={true} onDismiss={onRoleEditDismissHandler} />}
            {roleResponse && <RoleTable roleResponse={roleResponse} loading={loading} />}
            {error && (
                <Alert variant="destructive">
                    <InfoIcon className="h-4 w-4" />
                    <AlertTitle>Attention</AlertTitle>
                    <AlertDescription>
                        There was an error loading roles status: {error}
                    </AlertDescription>
                </Alert>
            )}
        </section>
    );
}
