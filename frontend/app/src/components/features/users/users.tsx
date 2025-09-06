import { PageHeader } from "@/components/shared/page-header";
import { UserTable } from "./user-table";
import { CreateNewUserDialog } from "./create-new-user-dialog";
import { useState } from "react";
import { useUsers } from "@/components/providers/users-provider";
import { UserEditDialog } from "@/components/features/users/user-edit-dialog";
import { UserDeleteDialog } from "@/components/features/users/user-delete-dialog";
import { useAuthContext } from "@/components/providers/auth-provider";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { InfoIcon } from 'lucide-react'


export function Users() {
    const { userResponse, refreshUsers, selectedUser, onSelectUser, loading, userError } = useUsers();
    const [isCreateNewUserDialogOpen, setIsCreateNewUserDialogOpen] = useState(false);
    const { can } = useAuthContext();
    const isAdmin = can("full:access");
    const isUserManager = can("user:read_and_write_only");

    const disableCreateNewRoleBtn = !isAdmin && !isUserManager;
    const onCreateNewUserDismissHandler = () => {
        refreshUsers();
        setIsCreateNewUserDialogOpen(false);
    }

    const onUserEditDismissHandler = () => {
        onSelectUser();
        refreshUsers();
    }
    return (
        <section>
            <PageHeader title="Users" subtitle="Manage your users" cta={{
                label: "Add User",
                onClick: () => setIsCreateNewUserDialogOpen(true),
                disabled: disableCreateNewRoleBtn
            }} />
            <CreateNewUserDialog open={isCreateNewUserDialogOpen} onDismiss={onCreateNewUserDismissHandler} />
            {selectedUser?.type === 'edit' && <UserEditDialog open={true} onDismiss={onUserEditDismissHandler} />}
            {selectedUser?.type === 'delete' && <UserDeleteDialog open={true} onDismiss={onUserEditDismissHandler} />}
            {userResponse && <UserTable userResponse={userResponse} loading={loading} />}
            {userError && (
                <Alert variant="destructive">
                    <InfoIcon className="h-4 w-4" />
                    <AlertTitle>Attention</AlertTitle>
                    <AlertDescription>
                        There was an error loading users status: {userError}
                    </AlertDescription>
                </Alert>
            )}
        </section>
    );
}