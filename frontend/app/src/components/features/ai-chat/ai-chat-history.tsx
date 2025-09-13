import { AIResponseSession } from "@/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardTitle } from "@/components/ui/card"
import { cn, getApiClient } from "@/lib/utils"
import { useEffect, useState } from "react"
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Menu } from 'lucide-react'
import { DropdownMenu, DropdownMenuItem, DropdownMenuContent, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { useSearchParams } from "react-router"

interface AIChatHistoryProps {
    mobile?: boolean
}
export function AIChatHistory({ mobile }: AIChatHistoryProps) {
    const [searchParams] = useSearchParams()
    const [history, setHistory] = useState<AIResponseSession[]>()
    const apiClient = getApiClient()

    async function fetchHistories() {
        const response = await apiClient.ai.getHistoryApiV1AiHistoryGet()
        setHistory(response)
    }
    useEffect(() => {
        fetchHistories()
    }, [])


    const histories = history || []
    function getTitle(historyId: string) {
        const historyItem = histories.find(h => h.sessions.find(s => s.id === historyId))?.sessions[0]
        return historyItem ? historyItem.histories[0].query : "Untitled"
    }
    if (mobile) {

        return (
            <section className="py-3 pr-3 md:hidden">
                <Card className="flex-flex flex-col h-full">
                    <CardTitle className="border-b border-primary/10 p-4">
                        Chat History
                    </CardTitle>
                    <CardContent className="p-4 overflow-auto">
                        <Select>
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Show History" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectGroup>
                                    {histories.map(history => (
                                        <SelectItem key={history.session_id} value={getTitle(history.history_id)}>
                                            {getTitle(history.history_id)} <br />
                                            {new Date(history.created_at).toLocaleString()}
                                        </SelectItem>
                                    ))}
                                </SelectGroup>
                            </SelectContent>
                        </Select>
                    </CardContent>
                </Card>
            </section>
        )
    }

    return (

        <section className="py-6 pr-3 w-xs hidden md:block">
            <section className="h-full space-y-3">
                <Card className="flex-flex flex-col h-full">
                    <CardTitle className="border-b border-primary/10 p-4">
                        Chat History
                    </CardTitle>
                    <CardContent className="p-4 overflow-auto">
                        <ul className=" text-sm font-medium">
                            {histories.map(history => (
                                <li key={history.session_id} className={cn("p-2 hover:bg-primary/5 cursor-pointer flex justify-between", {
                                    "bg-primary/5": history.session_id === searchParams.get("session_id")
                                })}>
                                    <div>
                                        <a href={`?history_id=${history.session_id}`} className="block w-full h-full">
                                            <div className="font-semibold">{getTitle(history.history_id)}</div>
                                            <div className="text-xs text-muted-foreground">{new Date(history.created_at).toLocaleString()}</div>
                                        </a>
                                    </div>
                                    <DropdownMenu>
                                        <DropdownMenuTrigger asChild>
                                            <Button size="icon" variant="ghost">
                                                <Menu className="h-4 w-4" />
                                            </Button>
                                        </DropdownMenuTrigger>
                                        <DropdownMenuContent align="start">
                                            <DropdownMenuItem>
                                                Delete
                                            </DropdownMenuItem>
                                        </DropdownMenuContent>
                                    </DropdownMenu>
                                </li>
                            ))}

                        </ul>
                    </CardContent>
                </Card>
            </section>
        </section>
    )
}