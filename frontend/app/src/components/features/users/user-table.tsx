import AdvanceTable from "@/components/shared/advance-table";
import { IResponseData } from "@/components/shared/iresponse-data.inteface";
import { TableActions } from "@/components/shared/table-actions";
import { UsersType } from "@/hooks/use-user";
import { createColumnHelper } from "@tanstack/react-table";



const columHelper = createColumnHelper<UsersType>();
const columns = [
    columHelper.accessor("id", {
        header: "Actions",
        cell: (c) => {
            return (
                <TableActions<typeof c.row.original>
                    options={[
                        {
                            label: "Edit",
                            data: c.row.original,
                            onClick: (data) => console.log("Edit", data),
                        },
                        {
                            label: "Delete",
                            data: c.row.original,
                            onClick: (data) => console.log("Delete", data),
                        },
                    ]}
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