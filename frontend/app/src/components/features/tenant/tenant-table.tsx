import { useAuthContext } from "@/components/providers/auth-provider";
import { TenantsType, useTenants } from "@/components/providers/tenant-provider";
import AdvanceTable from "@/components/shared/advance-table";
import { IResponseData } from "@/components/shared/iresponse-data.inteface";
import { ActionOption, TableActions } from "@/components/shared/table-actions";

import { createColumnHelper } from "@tanstack/react-table";



const columHelper = createColumnHelper<TenantsType>();
const columns = [
    columHelper.accessor("id", {
        header: "Actions",
        cell: (c) => {
            const { onSelectTenant } = useTenants()
            const { can } = useAuthContext()
            const isHostManageTenants = can("host:manage_tenants");
            const baseOptions: ActionOption<typeof c.row.original>[] = [
                {
                    label: "Edit",
                    data: c.row.original,
                    onClick: (data) => onSelectTenant({
                        type: 'edit',
                        tenant: data
                    }),
                    disabled: isHostManageTenants
                },
                {
                    label: "Delete",
                    data: c.row.original,
                    onClick: (data) => onSelectTenant({
                        type: 'delete',
                        tenant: data
                    }),
                    disabled: isHostManageTenants

                }
            ];
            return (
                <TableActions<typeof c.row.original>
                    options={baseOptions}
                    resource="tenant"
                />
            )
        }
    }),

    columHelper.accessor("name", {
        header: "Tenant Name",
    }),
    columHelper.accessor("subdomain", {
        header: "Subdomain",
    }),

];

interface TenantTableProps {
    tenantResponse: IResponseData<TenantsType>;
    loading?: boolean;
}

export function TenantTable({ tenantResponse, loading }: TenantTableProps) {
    return (
        <AdvanceTable<TenantsType> data={tenantResponse} columns={columns} loading={loading} />
    );
}