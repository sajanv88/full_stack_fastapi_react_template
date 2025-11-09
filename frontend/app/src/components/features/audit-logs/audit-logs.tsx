import { useAuditLogsContext } from "@/components/providers/audit-log-provider";
import { PageHeader } from "@/components/shared/page-header";
import { IconDownload } from "@tabler/icons-react";
import { AuditTable } from "./audit-table";

export function AuditLogs() {
    const { data, canDownloadAuditLogs, triggerDownloadAuditLogs } = useAuditLogsContext();
    async function downloadAuditLogs() {
        await triggerDownloadAuditLogs();
    }
    return (
        <section className="w-full 2xl:container 2xl:mx-auto ">
            <PageHeader title="Audit Logs" subtitle="View and Download your audit logs" cta={{
                label: "Download",
                onClick: () => downloadAuditLogs(),
                disabled: !canDownloadAuditLogs,
                icon: <IconDownload className="w-4 h-4" />
            }} />
            <AuditTable logs={data} />
        </section>
    )

}