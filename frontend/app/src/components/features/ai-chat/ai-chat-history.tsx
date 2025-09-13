import { AIResponse } from "@/api"
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
    const [histories, setHistories] = useState<AIResponse[]>([])
    const apiClient = getApiClient()

    async function fetchHistories() {
        const histories = await apiClient.ai.getHistoryApiV1AiHistoryGet()
        setHistories(histories)
    }
    useEffect(() => {
        fetchHistories()
    }, [])



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
                                        <SelectItem key={history.id} value={history.id}>
                                            {history.query || "Untitled"} <br />
                                            {new Date(history.timestamp).toLocaleString()}
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
                                <li key={history.id} className={cn("p-2 hover:bg-primary/5 cursor-pointer flex justify-between", {
                                    "bg-primary/5": history.id === searchParams.get("history_id")
                                })}>
                                    <div>
                                        <a href={`?history_id=${history.id}`} className="block w-full h-full">
                                            <div className="font-semibold">{history.query || "Untitled"}</div>
                                            <div className="text-xs text-muted-foreground">{new Date(history.timestamp).toLocaleString()}</div>
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