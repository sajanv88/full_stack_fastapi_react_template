import { PageHeader } from "@/components/shared/page-header";
import { UserTable } from "./user-table";
import { CreateNewUserDialog } from "./create-new-user-dialog";
import { useState } from "react";
import { useUsers } from "@/components/providers/users-provider";
import { UserEditDialog } from "@/components/features/users/user-edit-dialog";
import { UserDeleteDialog } from "@/components/features/users/user-delete-dialog";

export function Users() {
    const { userResponse, refreshUsers, selectedUser, selectUser } = useUsers();
    const [isCreateNewUserDialogOpen, setIsCreateNewUserDialogOpen] = useState(false);

    const onCreateNewUserDismissHandler = () => {
        refreshUsers();
        setIsCreateNewUserDialogOpen(false);
    }

    const onUserEditDismissHandler = () => {
        selectUser();
        refreshUsers();
    }
    return (
        <section>
            <PageHeader title="Users" subtitle="Manage your users" cta={{ label: "Add User", onClick: () => setIsCreateNewUserDialogOpen(true) }} />
            <CreateNewUserDialog open={isCreateNewUserDialogOpen} onDismiss={onCreateNewUserDismissHandler} />
            {selectedUser?.type === 'edit' && <UserEditDialog open={true} onDismiss={onUserEditDismissHandler} />}
            {selectedUser?.type === 'delete' && <UserDeleteDialog open={true} onDismiss={onUserEditDismissHandler} />}
            {userResponse && <UserTable userResponse={userResponse} />}
        </section>
    );
}