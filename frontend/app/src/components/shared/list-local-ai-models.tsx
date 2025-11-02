import { AIModelInfoDto } from "@/api";
import { useEffect, useState } from "react";
import {
    Select,
    SelectContent,
    SelectGroup,
    SelectItem,
    SelectLabel,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { InfoIcon, Brain, Cpu, Zap, Sparkles } from 'lucide-react'

interface ListLocalAIModelsProps {
    onModelSelect: (model: AIModelInfoDto) => void;
    selectedModel?: AIModelInfoDto;
    avilableModels: AIModelInfoDto[];
}
export function ListLocalAIModels({ onModelSelect, selectedModel, avilableModels }: ListLocalAIModelsProps) {
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);

    const getModelIcon = (modelName: string) => {
        if (modelName.toLowerCase().includes('gpt')) return <Brain className="h-4 w-4" />
        if (modelName.toLowerCase().includes('claude')) return <Sparkles className="h-4 w-4" />
        if (modelName.toLowerCase().includes('llama')) return <Zap className="h-4 w-4" />
        return <Cpu className="h-4 w-4" />
    }

    const formatModelSize = (size?: string) => {
        if (!size) return null
        return size.replace(/(\d+)([A-Z])/, '$1$2').toUpperCase()
    }

    useEffect(() => {
        if (!avilableModels) {
            setError("No AI models available. Please ensure your AI backend is configured correctly.");
            setLoading(false);
            return;
        }
    }, [avilableModels])

    if (error) {
        return (
            <Alert variant="destructive" className="w-full max-w-md">
                <InfoIcon className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
            </Alert>
        )
    }

    return (
        <div className="w-full md:max-w-sm">
            <div className="space-y-2">
                <div className="flex items-center space-x-2">
                    <Brain className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium text-muted-foreground">AI Model</span>
                </div>

                <Select
                    onValueChange={(value) => {
                        const selected = avilableModels.find(model => model.name === value);
                        if (selected) {
                            onModelSelect(selected);
                        }
                    }}
                    value={selectedModel?.name}
                >
                    <SelectTrigger className="w-full h-11 bg-background hover:bg-accent/50 transition-colors">
                        <SelectValue placeholder={
                            loading ? "Loading models..." : "Choose AI Model"
                        } />
                    </SelectTrigger>
                    <SelectContent className="w-full min-w-[300px]">
                        <SelectGroup>
                            <SelectLabel className="flex items-center space-x-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                                <Cpu className="h-3 w-3" />
                                <span>{loading ? "Fetching Models..." : "Available Models"}</span>
                            </SelectLabel>
                            {avilableModels.map((model) => (
                                <SelectItem
                                    key={model.name}
                                    value={model.name}
                                    className="cursor-pointer py-3"
                                >
                                    <div className="flex items-center justify-between w-full">
                                        <div className="flex items-center space-x-3">
                                            <div className="p-1.5 bg-primary/10 rounded-md">
                                                {getModelIcon(model.name)}
                                            </div>
                                            <div className="flex flex-col">
                                                <span className="font-medium text-sm">
                                                    {model.name}
                                                </span>
                                                {model.size && (
                                                    <span className="text-xs text-muted-foreground">
                                                        Model size: {formatModelSize(model.size)}
                                                    </span>
                                                )}
                                            </div>
                                        </div>
                                        {model.size && (
                                            <Badge variant="secondary" className="text-xs">
                                                {formatModelSize(model.size)}
                                            </Badge>
                                        )}
                                    </div>
                                </SelectItem>
                            ))}
                        </SelectGroup>
                    </SelectContent>
                </Select>


            </div>
        </div>
    )
}