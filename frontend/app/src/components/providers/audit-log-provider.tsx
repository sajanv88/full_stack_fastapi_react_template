import { AuditLogListDto } from "@/api";
import { createContext, useContext, useEffect, useState } from "react";
import { useAuthContext } from "./auth-provider";
import { getApiClient } from "@/lib/utils";
import { IResponseData } from "../shared/iresponse-data.inteface";
import { useSearchParams } from "react-router";
import { toast } from "sonner";

export type AuditLogType = AuditLogListDto["logs"][0];
export type AuditLogActionType = AuditLogType["action"];
interface AuditLogsProviderProps {
    children: React.ReactNode;
}

interface AuditLogsContextProps {
    data: IResponseData<AuditLogType>;
    canDownloadAuditLogs: boolean
    triggerDownloadAuditLogs: () => Promise<void>;
}

const initialState: AuditLogsContextProps = {
    data: {
        items: [],
        total: 0,
        skip: 0,
        limit: 10,
        hasNext: false,
        hasPrevious: false
    },
    canDownloadAuditLogs: false,
    triggerDownloadAuditLogs: async () => { }
};
const AuditLogsContext = createContext<AuditLogsContextProps>(initialState);

export function AuditLogProvider({ children }: AuditLogsProviderProps) {
    const [logs, setLogs] = useState<IResponseData<AuditLogType>>(initialState.data);
    const { accessToken, can } = useAuthContext();
    const [searchParams] = useSearchParams();

    const canDownloadAuditLogs = can("audit_logs:download") || can("full:access");
    async function fetchAuditLogs() {
        toast.dismiss();
        const skip = searchParams.get("skip");
        const limit = searchParams.get("limit");
        const action = searchParams.get("action") as string | null;
        try {
            const apiClient = getApiClient(accessToken);
            const response = await apiClient.auditLogs.listAuditLogsApiV1AuditLogsGet({
                skip: skip ? parseInt(skip) : 0,
                limit: limit ? parseInt(limit) : 10,
                action: action as AuditLogActionType
            });
            setLogs({
                items: response.logs,
                total: response.total,
                skip: response.skip,
                limit: response.limit,
                hasNext: response.has_next,
                hasPrevious: response.has_previous
            });
        } catch (error) {
            console.error("Failed to fetch audit logs:", error);
            toast.error("Failed to fetch audit logs", {
                richColors: true,
                duration: 5000,
                position: "top-right",
            });
        }
    }

    async function triggerDownloadAuditLogs() {
        toast.dismiss();
        try {
            const apiClient = getApiClient(accessToken);
            const response = await apiClient.auditLogs.downloadAuditLogsApiV1AuditLogsDownloadPost({
                action: searchParams.get("action") as AuditLogActionType | null
            });

            toast.success("Audit logs download requested", {
                richColors: true,
                duration: 5000,
                position: "top-right",
                description: response.message || "You will receive an email with the download link shortly."
            });
        } catch (error) {
            console.error("Failed to download audit logs:", error);
            toast.error("Failed to download audit logs", {
                richColors: true,
                duration: 5000,
                position: "top-right",
            });
        }
    }

    useEffect(() => {
        if (!accessToken) return;
        fetchAuditLogs();
    }, [accessToken, searchParams]);
    return (
        <AuditLogsContext.Provider value={{ data: logs, canDownloadAuditLogs, triggerDownloadAuditLogs }}>
            {children}
        </AuditLogsContext.Provider>
    );
}


export function useAuditLogsContext() {
    const context = useContext(AuditLogsContext);
    if (!context) {
        throw new Error("useAuditLogsContext must be used within an AuditLogsProvider");
    }
    return context;
}