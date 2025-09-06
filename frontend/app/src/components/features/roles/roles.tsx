import { useRoles } from "@/components/providers/roles-provider";
import { PageHeader } from "@/components/shared/page-header";
import { useState } from "react";
import { RoleTable } from "@/components/features/roles/role-table";
import { CreateNewRoleDialog } from "@/components/features/roles/create-new-role-dialog";
import { RoleDeleteDialog } from "@/components/features/roles/role-delete-dialog";
import { RoleEditDialog } from "@/components/features/roles/role-edit-dialog";
import { RoleManagePermissionDialog } from "@/components/features/roles/role-manage-permission-dialog";

export function Roles() {
    const { roleResponse, refreshRoles, selectedRole, onSelectRole } = useRoles();
    const [isCreateNewRoleDialogOpen, setIsCreateNewRoleDialogOpen] = useState(false);

    const onCreateNewRoleDismissHandler = () => {
        refreshRoles();
        setIsCreateNewRoleDialogOpen(false);
    }

    const onRoleEditDismissHandler = () => {
        onSelectRole();
        refreshRoles();
    }
    return (
        <section>
            <PageHeader title="Roles" subtitle="Manage your roles" cta={{ label: "Add Role", onClick: () => setIsCreateNewRoleDialogOpen(true) }} />
            <CreateNewRoleDialog open={isCreateNewRoleDialogOpen} onDismiss={onCreateNewRoleDismissHandler} />
            {selectedRole?.type === 'manage_permissions' && <RoleManagePermissionDialog open={true} onDismiss={onRoleEditDismissHandler} />}
            {selectedRole?.type === 'edit' && <RoleEditDialog open={true} onDismiss={onRoleEditDismissHandler} />}
            {selectedRole?.type === 'delete' && <RoleDeleteDialog open={true} onDismiss={onRoleEditDismissHandler} />}
            {roleResponse && <RoleTable roleResponse={roleResponse} />}
        </section>
    );
}
