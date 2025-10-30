import { useAuthContext } from "@/components/providers/auth-provider";
import { TenantsType, useTenants } from "@/components/providers/tenant-provider";
import AdvanceTable from "@/components/shared/advance-table";
import { IResponseData } from "@/components/shared/iresponse-data.inteface";
import { ActionOption, TableActions } from "@/components/shared/table-actions";

import { createColumnHelper } from "@tanstack/react-table";
import { NavLink } from "react-router";
import { IconExternalLink, IconCheck, IconCross, IconFidgetSpinner } from '@tabler/icons-react'
import { cn } from "@/lib/utils";
import { TenantDto } from "@/api";

function customDomainStatusIcon(status: TenantDto["custom_domain_status"]) {
    switch (status) {
        case "active":
            return <IconCheck className={cn("inline-block ml-1 mb-1 text-green-500")} size={14} title="Your domain is active." />
        case "failed":
            return <IconCross className={cn("inline-block ml-1 mb-1 text-red-500")} size={14} title="Your domain is not active." />
        case "activation-progress":
            return <IconFidgetSpinner
                className={cn("inline-block ml-1 mb-1 text-orange-400 animate-spin")}
                size={14} title="Your domain is being verified." />
        default:
            return null;
    }
}
const columHelper = createColumnHelper<TenantsType>();
const columns = [
    columHelper.accessor("id", {
        header: "Actions",
        cell: (c) => {
            const { onSelectTenant, onUpdateTenant } = useTenants()
            const { can } = useAuthContext()
            const isHostManageTenants = can("host:manage_tenants");
            const isActiveSubscription = !!c.row.original.subscription_id;

            const baseOptions: ActionOption<typeof c.row.original>[] = [

                {
                    label: "Delete",
                    data: c.row.original,
                    onClick: (data) => onSelectTenant({
                        type: 'delete',
                        tenant: data
                    }),
                    disabled: isHostManageTenants

                },
                {
                    label: "Manage Features",
                    data: c.row.original,
                    onClick: (data) => onSelectTenant({
                        type: 'manage_features',
                        tenant: data
                    }),
                    disabled: isHostManageTenants
                },
                {
                    label: c.row.original.is_active ? "Deactivate" : "Activate",
                    data: c.row.original,
                    onClick: async (data) => {
                        onUpdateTenant(data.id!, {
                            is_active: !data.is_active,
                            custom_domain: data.custom_domain
                        })
                    },
                    disabled: isHostManageTenants
                }

            ];

            if (!isActiveSubscription) {
                baseOptions.push({
                    label: "Manage Subscription",
                    data: c.row.original,
                    onClick: (data) => onSelectTenant({
                        type: 'manage_subscription',
                        tenant: data
                    }),
                    disabled: isHostManageTenants
                });
            }


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
        cell: (c) => {
            const subdomain = c.getValue();
            return subdomain ? (
                <NavLink to={`https://${subdomain}`} target="_blank" className="hover:underline">
                    {`https://${subdomain}`}
                    <IconExternalLink className="inline-block ml-1 mb-1" size={14} />

                </NavLink>
            ) : ("N/A")
        }
    }),
    columHelper.accessor("custom_domain", {
        header: "Custom Domain",
        cell: (c) => {
            const customDomain = c.getValue();
            return customDomain ? (
                <NavLink to={`https://${customDomain}`} target="_blank" className=" hover:underline">
                    {`https://${customDomain}`}
                    <IconExternalLink className="inline-block ml-1 mb-1" size={14} />
                    {customDomainStatusIcon(c.row.original.custom_domain_status!)}
                </NavLink>
            ) : ("N/A")
        }
    }),
    columHelper.accessor("is_active", {
        header: "Is Active",
        cell: (c) => c.getValue() ? "Yes" : "No",
    }),
    columHelper.accessor("subscription_id", {
        header: "Active Subscription",
        cell: (c) => c.getValue() || "N/A",
    })
];

interface TenantTableProps {
    tenantResponse: IResponseData<TenantsType>;
    loading?: boolean;
    errorMsg?: string;
}

export function TenantTable({ tenantResponse, loading, errorMsg }: TenantTableProps) {
    return (
        <AdvanceTable<TenantsType> data={tenantResponse} columns={columns} loading={loading} errorMsg={errorMsg} />
    );
}