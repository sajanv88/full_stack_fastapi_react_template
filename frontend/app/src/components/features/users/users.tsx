import { PageHeader } from "@/components/shared/page-header";
import { useUser } from "@/hooks/use-user";

export function Users() {
    const { userResponse, loading } = useUser();
    return (
        <section>
            <PageHeader title="Users" subtitle="Manage your users" cta={{ label: "Add User", onClick: () => { } }} />
            {loading ? (
                <p>Loading...</p>
            ) : (
                <ul>
                    {userResponse?.data.users.map(user => (
                        <li key={user.id}>{user.first_name}</li>
                    ))}
                </ul>
            )}
        </section>
    );
}