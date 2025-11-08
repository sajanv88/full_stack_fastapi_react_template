import { AuditLogListDto } from "@/api";
import { createContext, useContext, useEffect, useState } from "react";
import { useAuthContext } from "./auth-provider";
import { getApiClient } from "@/lib/utils";

interface AuditLogsProviderProps {
    children: React.ReactNode;
}

interface AuditLogsContextProps {
    data: AuditLogListDto
    canDownloadAuditLogs: boolean
}

const initialState: AuditLogsContextProps = {
    data: {
        logs: [],
        total: 0,
        skip: 0,
        limit: 10,
        has_next: false,
        has_previous: false
    },
    canDownloadAuditLogs: false
};
const AuditLogsContext = createContext<AuditLogsContextProps>(initialState);

export function AuditLogProvider({ children }: AuditLogsProviderProps) {
    const [logs, setLogs] = useState<AuditLogListDto>(initialState.data);
    const { accessToken, can } = useAuthContext();
    const canDownloadAuditLogs = can("audit_logs:download") || can("full:access");
    async function fetchAuditLogs() {
        try {
            const apiClient = getApiClient(accessToken);
            const response = await apiClient.auditLogs.listAuditLogsApiV1AuditLogsGet({
                skip: 0,
                limit: 100
            });
            setLogs(response);
        } catch (error) {
            console.error("Failed to fetch audit logs:", error);
        }
    }
    useEffect(() => {
        if (!accessToken) return;
        fetchAuditLogs();
    }, [accessToken]);
    return (
        <AuditLogsContext.Provider value={{ data: logs, canDownloadAuditLogs }}>
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