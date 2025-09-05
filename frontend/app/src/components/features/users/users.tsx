import { PageHeader } from "@/components/shared/page-header";
import { useUser } from "@/hooks/use-user";
import { UserTable } from "./user-table";
import { CreateNewUserDialog } from "./create-new-user-dialog";
import { useState } from "react";

export function Users() {
    const { userResponse } = useUser();
    const [isDialogOpen, setIsDialogOpen] = useState(false);

    const onDismissHandler = () => {
        window.location.reload();
        setIsDialogOpen(false);
    }
    return (
        <section>
            <PageHeader title="Users" subtitle="Manage your users" cta={{ label: "Add User", onClick: () => setIsDialogOpen(true) }} />
            <CreateNewUserDialog open={isDialogOpen} onDismiss={onDismissHandler} />
            {userResponse && <UserTable userResponse={userResponse} />}
        </section>
    );
}