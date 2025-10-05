import { Button } from "@/components/ui/button"
import { Card, CardContent, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
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
import { NavLink, useNavigate, useSearchParams } from "react-router"
import { useAIChat } from "@/components/providers/ai-chat-provider"
import { ScrollArea } from "@/components/ui/scroll-area"
import { toast } from "sonner"

interface AIChatHistoryProps {
    mobile?: boolean
}
export function AIChatHistory({ mobile }: AIChatHistoryProps) {
    const [searchParams, setSearchParams] = useSearchParams()
    const { sessions, onDeleteSession } = useAIChat()
    const navigate = useNavigate()
    const histories = sessions || []
    function getTitle(historyId: string) {
        const historyItem = histories.find(h => h.sessions.find(s => s.id === historyId))?.sessions[0]
        return historyItem ? historyItem.histories[0].query : "Untitled"
    }

    async function onDelete(sessionId: string) {
        try {
            await onDeleteSession(sessionId)
            toast.success("Session deleted successfully.", {
                richColors: true,
                position: "top-center",
                description: "The chat session has been deleted. All associated messages have been removed."
            })
            setSearchParams({})
        } catch (error) {
            console.error("Error deleting session:", error)
            toast.error("Failed to delete session.", {
                richColors: true,
                position: "top-center",
                description: "An error occurred while trying to delete the chat session. Please try again."
            })
        }

    }
    if (mobile) {

        return (
            <section className="py-3 md:pr-3 md:hidden">
                <Card className="flex-flex flex-col h-full">
                    <CardTitle className="border-b border-primary/10 p-4">
                        Chat History
                    </CardTitle>
                    <CardContent className="p-4 overflow-auto">
                        <Select onValueChange={(value) => {
                            navigate(`?session_id=${value}`)
                        }}>
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Show History" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectGroup>
                                    {histories.map(history => (
                                        <SelectItem key={history.session_id} value={history.session_id}>
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
                    <CardContent className="p-4">
                        <ScrollArea className="h-[700px]">
                            <ul className=" text-sm font-medium pr-4">
                                {histories.map(history => (
                                    <li key={history.session_id} className={cn("p-2 hover:bg-primary/5 cursor-pointer flex justify-between", {
                                        "bg-primary/5": history.session_id === searchParams.get("session_id")
                                    })}>
                                        <div>
                                            <NavLink to={`?session_id=${history.session_id}`} className="block w-full h-full">
                                                <div className="font-semibold">{getTitle(history.history_id)}</div>
                                                <div className="text-xs text-muted-foreground">{new Date(history.created_at).toLocaleString()}</div>
                                            </NavLink>
                                        </div>
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button size="icon" variant="ghost">
                                                    <Menu className="h-4 w-4" />
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="start">
                                                <DropdownMenuItem onClick={() => onDelete(history.session_id)}>
                                                    Delete
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </li>
                                ))}

                            </ul>
                        </ScrollArea>
                    </CardContent>
                </Card>
            </section>
        </section>
    )
}