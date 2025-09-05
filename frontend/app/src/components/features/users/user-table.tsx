import { UsersType, useUsers } from "@/components/providers/users-provider";
import AdvanceTable from "@/components/shared/advance-table";
import { IResponseData } from "@/components/shared/iresponse-data.inteface";
import { ActionOption, TableActions } from "@/components/shared/table-actions";
import { createColumnHelper } from "@tanstack/react-table";



const columHelper = createColumnHelper<UsersType>();
const columns = [
    columHelper.accessor("id", {
        header: "Actions",
        cell: (c) => {
            const { selectUser } = useUsers()
            const actionOptions: ActionOption<typeof c.row.original> = {
                label: "Resend Activation Email",
                data: c.row.original,
                onClick: (data) => selectUser({
                    type: 'resend_email',
                    user: data
                }),
            }

            const baseOptions: ActionOption<typeof c.row.original>[] = [
                {
                    label: "Edit",
                    data: c.row.original,
                    onClick: (data) => selectUser({
                        type: 'edit',
                        user: data
                    }),
                },
                {
                    label: "Delete",
                    data: c.row.original,
                    onClick: (data) => selectUser({
                        type: 'delete',
                        user: data
                    }),
                }
            ];

            // Add "Resend Activation Email" option only for inactive users
            const options = !c.row.original.is_active
                ? [...baseOptions, actionOptions]
                : baseOptions;

            return (
                <TableActions<typeof c.row.original>
                    options={options}
                />
            )
        }
    }),
    columHelper.accessor("first_name", {
        header: "First Name",
    }),
    columHelper.accessor("last_name", {
        header: "Last Name",
    }),
    columHelper.accessor("email", {
        header: "Email",
    }),
    columHelper.accessor("is_active", {
        header: "Active",
    }),
];



interface UserTableProps {
    userResponse: IResponseData<UsersType>;
}
export function UserTable({ userResponse }: UserTableProps) {
    return (
        <AdvanceTable<UsersType> data={userResponse} columns={columns} />
    );
}