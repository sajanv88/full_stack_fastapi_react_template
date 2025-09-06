import { Permission } from "@/api";
import { RolesType, useRoles } from "@/components/providers/roles-provider";
import AdvanceTable from "@/components/shared/advance-table";
import { IResponseData } from "@/components/shared/iresponse-data.inteface";
import { ActionOption, TableActions } from "@/components/shared/table-actions";
import { Badge } from "@/components/ui/badge";
import { createColumnHelper } from "@tanstack/react-table";



const columHelper = createColumnHelper<RolesType>();
const columns = [
    columHelper.accessor("id", {
        header: "Actions",
        cell: (c) => {
            const { onSelectRole } = useRoles()
            const actionOptions: ActionOption<typeof c.row.original>[] = [
                {
                    label: "Clone",
                    data: c.row.original,
                    onClick: (data) => onSelectRole({
                        type: 'clone',
                        role: data
                    }),
                },
                {
                    label: "Manage Permissions",
                    data: c.row.original,
                    onClick: (data) => onSelectRole({
                        type: 'manage_permissions',
                        role: data
                    }),
                }
            ]

            const baseOptions: ActionOption<typeof c.row.original>[] = [
                {
                    label: "Edit",
                    data: c.row.original,
                    onClick: (data) => onSelectRole({
                        type: 'edit',
                        role: data
                    }),
                },
                {
                    label: "Delete",
                    data: c.row.original,
                    onClick: (data) => onSelectRole({
                        type: 'delete',
                        role: data
                    }),
                }
            ];


            // Add "Clone" option only for non admin users
            const options = !c.row.original.name.toLowerCase().includes('admin')
                ? [...baseOptions, ...actionOptions]
                : baseOptions;

            return (
                <TableActions<typeof c.row.original>
                    options={options}
                    resource="role"
                />
            )
        }
    }),

    columHelper.accessor("name", {
        header: "Role Name",
    }),
    columHelper.accessor("description", {
        header: "Description",
    }),
    columHelper.accessor("permissions", {
        header: "Permissions",
        cell: (c) => {
            const permissions: Array<Permission> = c.row.original.permissions ?? [];
            return (
                <ul className="flex flex-wrap max-w-2xs">
                    {permissions.map((perm) => (
                        <Badge key={perm} variant="outline" className="m-1">
                            {perm}
                        </Badge>
                    ))}
                </ul>
            );
        }
    }),

];



interface RoleTableProps {
    roleResponse: IResponseData<RolesType>;
}
export function RoleTable({ roleResponse }: RoleTableProps) {
    return (
        <AdvanceTable<RolesType> data={roleResponse} columns={columns} />
    );
}