import React, { useState, useRef, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Loading } from '@/components/shared/loading'
import { cn, getAccessToken } from '@/lib/utils'
import { Send, Bot, User, Sparkles, Copy, RefreshCw, Trash2 } from 'lucide-react'
import { useAuthContext } from '@/components/providers/auth-provider'
import { ListLocalAIModels } from '@/components/shared/list-local-ai-models'
import { AIRequest, ModelsResponse } from '@/api'

interface Message {
    id: string
    content: string
    role: 'user' | 'assistant'
    timestamp: Date
    isStreaming?: boolean
}

interface ChatState {
    messages: Message[]
    isLoading: boolean
    error: string | null
}

export function AIChat() {
    const { user } = useAuthContext()
    const [chatState, setChatState] = useState<ChatState>({
        messages: [],
        isLoading: false,
        error: null
    })
    const [selectedModel, setSelectedModel] = useState<ModelsResponse>()
    const [input, setInput] = useState('')
    const scrollAreaRef = useRef<HTMLDivElement>(null)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLTextAreaElement>(null)

    // Auto-resize textarea
    const adjustTextareaHeight = () => {
        const textarea = inputRef.current
        if (textarea) {
            textarea.style.height = 'auto'
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
        }
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(e.target.value)
        adjustTextareaHeight()
    }

    // Auto-scroll to bottom when new messages arrive or content changes
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [chatState.messages])

    // Also scroll when streaming content changes
    useEffect(() => {
        if (chatState.isLoading) {
            const timer = setInterval(scrollToBottom, 100)
            return () => clearInterval(timer)
        }
    }, [chatState.isLoading])

    // Focus input on mount
    useEffect(() => {
        inputRef.current?.focus()
    }, [])

    const generateId = () => Math.random().toString(36).substr(2, 9)

    const sendMessage = async () => {
        if (!input.trim() || chatState.isLoading) return

        const userMessage: Message = {
            id: generateId(),
            content: input.trim(),
            role: 'user',
            timestamp: new Date()
        }

        const assistantMessage: Message = {
            id: generateId(),
            content: '',
            role: 'assistant',
            timestamp: new Date(),
            isStreaming: true
        }

        setChatState(prev => ({
            ...prev,
            messages: [...prev.messages, userMessage, assistantMessage],
            isLoading: true,
            error: null
        }))

        setInput('')

        // Reset textarea height
        const textarea = inputRef.current
        if (textarea) {
            textarea.style.height = 'auto'
        }

        try {
            const accessToken = getAccessToken();

            const payload: AIRequest = {
                question: userMessage.content,
                model_name: selectedModel?.name
            }
            const response = await fetch('/api/v1/ai/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${accessToken}`
                },
                body: JSON.stringify(payload)
            })
            if (!response.ok) throw new Error(response.statusText + " Check if you have selected AI Model.")
            if (!response.body) throw new Error('No response body.')

            const reader = response.body.getReader()

            let accumulatedContent = ''

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                const chunk = new TextDecoder().decode(value, { stream: true })
                accumulatedContent += chunk

                setChatState(prev => ({
                    ...prev,
                    messages: prev.messages.map(msg =>
                        msg.id === assistantMessage.id
                            ? { ...msg, content: accumulatedContent }
                            : msg
                    )
                }))
            }

            // Mark streaming as complete
            setChatState(prev => ({
                ...prev,
                messages: prev.messages.map(msg =>
                    msg.id === assistantMessage.id
                        ? { ...msg, isStreaming: false }
                        : msg
                ),
                isLoading: false
            }))

        } catch (error) {
            setChatState(prev => ({
                ...prev,
                messages: prev.messages.filter(msg => msg.id !== assistantMessage.id),
                isLoading: false,
                error: error instanceof Error ? error.message : 'An error occurred'
            }))
        }
    }

    const clearChat = () => {
        setChatState({
            messages: [],
            isLoading: false,
            error: null
        })
    }

    const copyMessage = (content: string) => {
        navigator.clipboard.writeText(content)
    }

    const retryLastMessage = () => {
        if (chatState.messages.length > 0) {
            const lastUserMessage = [...chatState.messages].reverse().find(m => m.role === 'user')
            if (lastUserMessage) {
                setInput(lastUserMessage.content)
                // Adjust textarea height after setting content
                setTimeout(adjustTextareaHeight, 0)
                // Remove the last assistant message if it exists
                setChatState(prev => ({
                    ...prev,
                    messages: prev.messages.filter((msg, index, arr) =>
                        !(msg.role === 'assistant' && index === arr.length - 1)
                    )
                }))
            }
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
        // Shift+Enter is handled naturally by textarea for new lines
    }

    return (
        <div className="h-full flex flex-col">
            {/* Page Header */}
            <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="container mx-auto px-3 sm:px-4 py-4 sm:py-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2 sm:space-x-3">
                            <div className="p-2 sm:p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
                                <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                            </div>
                            <div className="min-w-0 flex-1">
                                <h1 className="text-lg sm:text-2xl font-bold truncate">AI Assistant</h1>
                                <div className="flex items-center space-x-2">
                                    <p className="text-muted-foreground text-sm sm:text-base hidden sm:block">
                                        Chat with our intelligent AI assistant
                                    </p>

                                </div>
                                {selectedModel && (
                                    <Badge variant="secondary" className="text-xs bg-primary/10 hover:bg-primary/20">
                                        <div className="w-2 h-2 bg-green-500 rounded-full mr-1.5"></div>
                                        {selectedModel.name}
                                    </Badge>
                                )}
                            </div>
                        </div>

                        <div className="flex items-center space-x-3 sm:space-x-4">
                            <div className="hidden sm:block">
                                <ListLocalAIModels
                                    onModelSelect={setSelectedModel}
                                    selectedModel={selectedModel}
                                />
                            </div>

                            <div className="flex space-x-1 sm:space-x-2 mt-6">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={retryLastMessage}
                                    disabled={chatState.isLoading || chatState.messages.length === 0}
                                    className="hidden sm:flex"
                                >
                                    <RefreshCw className="w-4 h-4 sm:mr-2" />
                                    <span className="hidden sm:inline">Retry</span>
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={retryLastMessage}
                                    disabled={chatState.isLoading || chatState.messages.length === 0}
                                    className="sm:hidden"
                                >
                                    <RefreshCw className="w-4 h-4" />
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={clearChat}
                                    disabled={chatState.isLoading}
                                    className="hidden sm:flex"
                                >
                                    <Trash2 className="w-4 h-4 sm:mr-2" />
                                    <span className="hidden sm:inline">Clear</span>
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={clearChat}
                                    disabled={chatState.isLoading}
                                    className="sm:hidden"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </Button>
                            </div>
                        </div>

                        {/* Mobile Model Selection */}
                        <div className="sm:hidden mt-4">
                            <ListLocalAIModels
                                onModelSelect={setSelectedModel}
                                selectedModel={selectedModel}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Chat Container */}
            <div className="flex-1 container w-full mx-auto py-3 sm:py-6">
                <div className="flex flex-col h-full space-y-3 sm:space-y-4">
                    {/* Chat Messages */}
                    <Card className="flex-1 flex flex-col">
                        <CardContent className="flex-1 p-0">
                            <ScrollArea className="h-[calc(100vh-280px)] sm:h-[600px] p-3 sm:p-6" ref={scrollAreaRef}>
                                {chatState.messages.length === 0 ? (
                                    <div className="flex flex-col items-center justify-center h-full text-center space-y-4 sm:space-y-6 px-4">
                                        <div className="p-4 sm:p-6 bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900/20 dark:to-purple-900/20 rounded-full">
                                            <Bot className="w-8 h-8 sm:w-12 sm:h-12 text-blue-600" />
                                        </div>
                                        <div className="max-w-md">
                                            <h3 className="text-lg sm:text-xl font-semibold mb-2">Welcome to AI Chat</h3>
                                            <p className="text-muted-foreground text-sm sm:text-base">
                                                Start a conversation with our AI assistant. Ask questions, get help with coding, brainstorm ideas, or just have a friendly chat!
                                            </p>
                                        </div>
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 max-w-md w-full">
                                            {[
                                                "What can you help me with?",
                                                "Explain quantum computing",
                                                "Write a Python function",
                                                "Help me brainstorm ideas"
                                            ].map((suggestion, index) => (
                                                <Button
                                                    key={index}
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => {
                                                        setInput(suggestion)
                                                        setTimeout(adjustTextareaHeight, 0)
                                                    }}
                                                    className="justify-start h-auto p-2 sm:p-3 text-left whitespace-normal text-xs sm:text-sm"
                                                >
                                                    {suggestion}
                                                </Button>
                                            ))}
                                        </div>
                                    </div>
                                ) : (
                                    <div className="space-y-4 sm:space-y-6">
                                        {chatState.messages.map((message) => (
                                            <div
                                                key={message.id}
                                                className={cn(
                                                    "flex space-x-2 sm:space-x-4",
                                                    message.role === 'user' ? 'justify-end' : 'justify-start'
                                                )}
                                            >
                                                {message.role === 'assistant' && (
                                                    <Avatar className="w-6 h-6 sm:w-8 sm:h-8 mt-1 flex-shrink-0">
                                                        <AvatarFallback className="bg-gradient-to-r from-blue-500 to-purple-600">
                                                            <Bot className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                                                        </AvatarFallback>
                                                    </Avatar>
                                                )}

                                                <div
                                                    className={cn(
                                                        "max-w-[85%] sm:max-w-[75%] rounded-xl px-3 sm:px-4 py-2 sm:py-3 break-words group relative",
                                                        message.role === 'user'
                                                            ? 'bg-primary text-primary-foreground ml-auto'
                                                            : 'bg-muted hover:bg-muted/80 transition-colors'
                                                    )}
                                                >
                                                    <div className="whitespace-pre-wrap text-sm leading-relaxed">
                                                        {message.content}
                                                    </div>
                                                    {message.isStreaming && (
                                                        <div className="mt-2 sm:mt-3 flex items-center space-x-2">
                                                            <Loading variant="dots" size="sm" />
                                                            <span className="text-xs opacity-70">AI is typing...</span>
                                                        </div>
                                                    )}

                                                    {/* Message actions */}
                                                    {!message.isStreaming && message.content && (
                                                        <div className="flex items-center justify-between mt-2 border-t border-border/50">
                                                            <span className="text-xs ">
                                                                {message.timestamp.toLocaleTimeString()}
                                                            </span>
                                                            <Button
                                                                variant="ghost"
                                                                size="sm"
                                                                onClick={() => copyMessage(message.content)}
                                                                className="h-6 sm:h-7 px-1 sm:px-2 text-xs "
                                                            >
                                                                <Copy className="w-3 h-3 sm:mr-1" />
                                                                <span className="hidden sm:inline">Copy</span>
                                                            </Button>
                                                        </div>
                                                    )}
                                                </div>

                                                {message.role === 'user' && (
                                                    <Avatar className="w-6 h-6 sm:w-8 sm:h-8 mt-1 flex-shrink-0">
                                                        <AvatarImage src={user?.image_url ?? "https://github.com/evilrabbit.png"} alt={user?.last_name} />
                                                        <AvatarFallback className="bg-primary">
                                                            <User className="w-3 h-3 sm:w-4 sm:h-4 text-primary-foreground" />
                                                        </AvatarFallback>
                                                    </Avatar>
                                                )}
                                            </div>
                                        ))}
                                        {/* Invisible div for scrolling to bottom */}
                                        <div ref={messagesEndRef} />
                                    </div>
                                )}
                            </ScrollArea>
                        </CardContent>
                    </Card>

                    {/* Error Display */}
                    {chatState.error && (
                        <Card className="border-destructive bg-destructive/5">
                            <CardContent className="p-3 sm:p-4">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-2 text-destructive">
                                        <span className="text-sm font-medium">Error: {chatState.error}</span>
                                    </div>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => setChatState(prev => ({ ...prev, error: null }))}
                                    >
                                        Dismiss
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {/* Input Area */}
                    <Card className="border-2 border-dashed border-muted-foreground/25 hover:border-muted-foreground/50 transition-colors">
                        <CardContent className="p-3 sm:p-4">
                            <div className="flex space-x-2 sm:space-x-3">
                                <div className="flex-1 relative">
                                    <Textarea
                                        ref={inputRef}
                                        value={input}
                                        onChange={handleInputChange}
                                        onKeyPress={handleKeyPress}
                                        placeholder="Type your message..."
                                        disabled={chatState.isLoading}
                                        className="pr-8 sm:pr-12 min-h-[40px] sm:min-h-[44px] max-h-[120px] text-sm sm:text-base resize-none"
                                        maxLength={2000}
                                        rows={1}
                                    />
                                    {chatState.isLoading && (
                                        <div className="absolute right-2 sm:right-3 top-1/2 transform -translate-y-1/2">
                                            <Loading variant="spinner" size="sm" />
                                        </div>
                                    )}
                                </div>
                                <Button
                                    onClick={sendMessage}
                                    disabled={!input.trim() || chatState.isLoading}
                                    className="px-3 sm:px-6 h-10 sm:h-11"
                                    size="default"
                                >
                                    <Send className="w-4 h-4 sm:mr-2" />
                                    <span className="hidden sm:inline">Send</span>
                                </Button>
                            </div>
                            <div className="flex items-center justify-between mt-2 sm:mt-3 text-xs text-muted-foreground">
                                <span className="hidden sm:inline">Press Enter to send • Shift+Enter for new line</span>
                                <span className="sm:hidden">Enter to send</span>
                                <span className={cn(
                                    "font-mono",
                                    input.length > 1800 && "text-orange-500",
                                    input.length > 1950 && "text-destructive"
                                )}>
                                    {input.length}/2000
                                </span>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}
