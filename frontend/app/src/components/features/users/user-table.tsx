import AdvanceTable from "@/components/shared/advance-table";
import { IResponseData } from "@/components/shared/iresponse-data.inteface";
import { Button } from "@/components/ui/button";
import { UsersType } from "@/hooks/use-user";
import { createColumnHelper } from "@tanstack/react-table";
import { CogIcon } from 'lucide-react'



const columHelper = createColumnHelper<UsersType>();
const columns = [
    columHelper.accessor("id", {
        header: "Actions",
        cell: (c) => {
            return (
                <Button>
                    <CogIcon className="h-4 w-4" />
                    Actions
                </Button>
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