import { useAuthContext } from "@/components/providers/auth-provider";
import { PageHeader } from "@/components/shared/page-header";
import { useState } from "react";
import { TenantTable } from "./tenant-table";
import { useTenants } from "@/components/providers/tenant-provider";

export function Tenants() {
    const [isCreateNewTenantDialogOpen, setIsCreateNewTenantDialogOpen] = useState(false);
    const { can } = useAuthContext();
    const isHost = can("host:manage_tenants");
    const isAdmin = can("full:access");
    const { tenantResponse, isLoading } = useTenants();

    const disableCreateNewTenantBtn = !isHost && !isAdmin;

    return (
        <section>
            <PageHeader title="Tenants" subtitle="Manage your tenants" cta={{
                label: "Add Tenant",
                onClick: () => setIsCreateNewTenantDialogOpen(true),
                disabled: disableCreateNewTenantBtn
            }} />
            {tenantResponse && <TenantTable tenantResponse={tenantResponse} loading={isLoading} />}
        </section>
    )
}