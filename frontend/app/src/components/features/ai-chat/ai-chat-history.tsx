import { AIResponse } from "@/api"
import { Card, CardContent, CardTitle } from "@/components/ui/card"
import { getApiClient } from "@/lib/utils"
import { useEffect, useState } from "react"

export function AIChatHistory() {
    const [histories, setHistories] = useState<AIResponse[]>([])
    async function fetchHistories() {
        const apiClient = getApiClient()
        const histories = await apiClient.ai.getHistoryApiV1AiHistoryGet()
        setHistories(histories)
    }
    useEffect(() => {
        fetchHistories()
    }, [])

    return (
        <section className="py-3 pr-3 sm:py-6">
            <section className="h-full space-y-3 sm:space-y-4">
                <Card className="flex-1 flex flex-col h-full">
                    <CardTitle className="border-b border-primary/10 p-4">
                        Chat History
                    </CardTitle>
                    <CardContent className="p-4 overflow-auto">
                        <ul className=" text-sm font-medium">
                            {histories.map(history => (
                                <li key={history.id} className="p-2 hover:bg-primary/5 cursor-pointer">
                                    <a href={`?history_id=${history.id}`} className="block w-full h-full">
                                        <div className="font-semibold">{history.query || "Untitled"}</div>
                                        <div className="text-xs text-muted-foreground">{new Date(history.timestamp).toLocaleString()}</div>
                                    </a>
                                </li>
                            ))}

                        </ul>
                    </CardContent>
                </Card>
            </section>
        </section>
    )
}