import { AISessionByUserIdDto } from "@/api";
import { getApiClient } from "@/lib/utils";
import { createContext, useContext, useEffect, useState } from "react"

type AIChatProviderState = {
    fetchAllSessions: () => Promise<void>;
    sessions: AISessionByUserIdDto[];
    onDeleteSession: (sessionId: string) => Promise<void>;
}

const AIChatContext = createContext<AIChatProviderState>({
    fetchAllSessions: async () => { },
    sessions: [],
    onDeleteSession: async () => { }
})

interface AIChatProviderProps {
    children: React.ReactNode;
}

export function AIChatProvider({ children }: AIChatProviderProps) {
    const [sessions, setSessions] = useState<AISessionByUserIdDto[]>([]);
    const apiClient = getApiClient()

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

    useEffect(() => {
        fetchAllSessions();
    }, [])

    return (
        <AIChatContext.Provider value={{ fetchAllSessions, sessions, onDeleteSession }}>
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