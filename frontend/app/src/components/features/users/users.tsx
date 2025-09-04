import { PageHeader } from "@/components/shared/page-header";
import { useUser } from "@/hooks/use-user";
import { UserTable } from "./user-table";

export function Users() {
    const { userResponse, loading } = useUser();
    return (
        <section>
            <PageHeader title="Users" subtitle="Manage your users" cta={{ label: "Add User", onClick: () => { } }} />
            {userResponse && <UserTable userResponse={userResponse} />}
        </section>
    );
}