import { AuditLogType } from "@/components/providers/audit-log-provider";
import AdvanceTable from "@/components/shared/advance-table";
import { IResponseData } from "@/components/shared/iresponse-data.inteface";
import { createColumnHelper } from "@tanstack/react-table";

const columnHelper = createColumnHelper<AuditLogType>();
const columns = [
    columnHelper.accessor("entity", {
        header: "Entity",
        cell: info => info.getValue(),
    }),
    columnHelper.accessor("action", {
        header: "Action",
        cell: info => info.getValue(),
    }),
    columnHelper.accessor("user_id", {
        header: "Performed By",
        cell: info => info.getValue(),
    }),
    columnHelper.accessor("timestamp", {
        header: "Timestamp",
        cell: info => new Date(info.getValue()!).toLocaleString(),
    }),
    columnHelper.accessor("changes", {
        header: "Details",
        cell: info => JSON.stringify(info.getValue()),
    }),
    columnHelper.accessor("tenant_id", {
        header: "Tenant ID",
        cell: info => info.getValue(),
    }),

]
interface AuditTableProps {
    logs: IResponseData<AuditLogType>;
    loading?: boolean;
    errorMsg?: string;
}
export function AuditTable({ logs, loading, errorMsg }: AuditTableProps) {
    return (
        <AdvanceTable<AuditLogType>
            data={logs}
            columns={columns}
            loading={loading}
            errorMsg={errorMsg}
            dropdownActions={{
                options: [
                    { name: "Read", value: "read" },
                    { name: "Update", value: "update" },
                    { name: "Delete", value: "delete" },
                    { name: "Create", value: "create" },
                    { name: "Error", value: "error" },
                    { name: "Login", value: "login" },
                    { name: "Logout", value: "logout" },
                ],
            }}
        />
    )
}