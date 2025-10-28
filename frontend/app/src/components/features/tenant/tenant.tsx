import { useAuthContext } from "@/components/providers/auth-provider";
import { PageHeader } from "@/components/shared/page-header";
import { useState } from "react";
import { TenantTable } from "@/components/features/tenant/tenant-table";
import { useTenants } from "@/components/providers/tenant-provider";
import { CreateNewTenantDialog } from "@/components/features/tenant/create-new-tenant-dialog";
import { TenantDeleteDialog } from "@/components/features/tenant/tenant-delete-dialog";
import { ManageFeature } from "@/components/features/tenant/manage-feature";

export function Tenants() {
    const [isCreateNewTenantDialogOpen, setIsCreateNewTenantDialogOpen] = useState(false);
    const { can } = useAuthContext();
    const isHost = can("host:manage_tenants");
    const isAdmin = can("full:access");
    const { tenantResponse, isLoading, onSelectTenant, selectedTenant } = useTenants();

    const disableCreateNewTenantBtn = !isHost && !isAdmin;
    const errorMsg = !isHost ? "You do not have permission to view this resource." : undefined
    const onTenantDismissHandler = () => {
        onSelectTenant();
    }
    return (
        <section className="w-full 2xl:container 2xl:mx-auto ">
            <PageHeader title="Tenants" subtitle="Manage your tenants" cta={{
                label: "Add Tenant",
                onClick: () => setIsCreateNewTenantDialogOpen(true),
                disabled: disableCreateNewTenantBtn
            }} />
            <CreateNewTenantDialog open={isCreateNewTenantDialogOpen} onDismiss={() => setIsCreateNewTenantDialogOpen(false)} />
            {selectedTenant?.type === 'delete' && <TenantDeleteDialog open={true} onDismiss={onTenantDismissHandler} />}

            {selectedTenant?.type === 'manage_features' && <ManageFeature open={true} onDismiss={onTenantDismissHandler} />}
            {tenantResponse && <TenantTable tenantResponse={tenantResponse} loading={isLoading} errorMsg={errorMsg} />}
        </section>
    )
}