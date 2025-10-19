import { AISessionByUserIdDto } from "@/api";
import { getApiClient } from "@/lib/utils";
import { createContext, useContext, useEffect, useState } from "react"
import { useAuthContext } from "./auth-provider";
import { toast } from "sonner";

type AIChatProviderState = {
    fetchAllSessions: () => Promise<void>;
    sessions: AISessionByUserIdDto[];
    onDeleteSession: (sessionId: string) => Promise<void>;
    getAIChatNewSession: () => Promise<string>;
}

const AIChatContext = createContext<AIChatProviderState>({
    fetchAllSessions: async () => { },
    sessions: [],
    onDeleteSession: async () => { },
    getAIChatNewSession: async () => { throw new Error("Not implemented"); }
})

interface AIChatProviderProps {
    children: React.ReactNode;
}

export function AIChatProvider({ children }: AIChatProviderProps) {
    const [sessions, setSessions] = useState<AISessionByUserIdDto[]>([]);
    const { accessToken } = useAuthContext();
    const apiClient = getApiClient(accessToken)

    async function fetchAllSessions() {
        const response = await apiClient.ai.getHistoryApiV1AiHistoryGet();
        setSessions(response);
    }

    async function onDeleteSession(sessionId: string) {
        await apiClient.ai.deleteSessionApiV1AiSessionsSessionIdDelete({
            sessionId
        });
        await fetchAllSessions();
    }

    async function getAIChatNewSession() {
        try {
            const response = await apiClient.ai.createNewSessionApiV1AiNewSessionGet();
            return response.session_id;
        } catch (error) {
            console.error("Failed to create new AI session:", error);
            toast.error("Failed to create new AI session", { richColors: true, position: "top-right" });
            throw new Error("Failed to create new AI session");
        }
    }

    useEffect(() => {
        fetchAllSessions();
    }, [accessToken])

    return (
        <AIChatContext.Provider value={{ fetchAllSessions, sessions, onDeleteSession, getAIChatNewSession }}>
            {children}
        </AIChatContext.Provider>
    )
}

export function useAIChat() {
    const context = useContext(AIChatContext);
    if (!context) {
        throw new Error("useAIChat must be used within an AIChatProvider");
    }
    return context;
}