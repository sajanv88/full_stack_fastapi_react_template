import { cn } from "@/lib/utils"

interface LoadingProps {
    variant?: "spinner" | "dots" | "pulse" | "skeleton"
    size?: "sm" | "md" | "lg"
    text?: string
    className?: string
}

export function Loading({
    variant = "spinner",
    size = "md",
    text,
    className
}: LoadingProps) {
    const sizeClasses = {
        sm: "w-4 h-4",
        md: "w-8 h-8",
        lg: "w-12 h-12"
    }

    if (variant === "spinner") {
        return (
            <div className={cn("flex flex-col items-center justify-center gap-3", className)}>
                <div className={cn(
                    "animate-spin rounded-full border-2 border-gray-300 border-t-blue-600",
                    sizeClasses[size]
                )} />
                {text && (
                    <p className="text-sm text-gray-600 animate-pulse">{text}</p>
                )}
            </div>
        )
    }

    if (variant === "dots") {
        return (
            <div className={cn("flex flex-col items-center justify-center gap-3", className)}>
                <div className="flex space-x-1">
                    <div className={cn(
                        "bg-blue-600 rounded-full animate-bounce [animation-delay:0ms]",
                        size === "sm" ? "w-2 h-2" : size === "md" ? "w-3 h-3" : "w-4 h-4"
                    )} />
                    <div className={cn(
                        "bg-blue-600 rounded-full animate-bounce [animation-delay:150ms]",
                        size === "sm" ? "w-2 h-2" : size === "md" ? "w-3 h-3" : "w-4 h-4"
                    )} />
                    <div className={cn(
                        "bg-blue-600 rounded-full animate-bounce [animation-delay:300ms]",
                        size === "sm" ? "w-2 h-2" : size === "md" ? "w-3 h-3" : "w-4 h-4"
                    )} />
                </div>
                {text && (
                    <p className="text-sm text-gray-600 animate-pulse">{text}</p>
                )}
            </div>
        )
    }

    if (variant === "pulse") {
        return (
            <div className={cn("flex flex-col items-center justify-center gap-3", className)}>
                <div className={cn(
                    "bg-gradient-to-r from-blue-500 to-purple-600 rounded-full animate-pulse",
                    sizeClasses[size]
                )} />
                {text && (
                    <p className="text-sm text-gray-600 animate-pulse">{text}</p>
                )}
            </div>
        )
    }

    if (variant === "skeleton") {
        return (
            <div className={cn("space-y-3", className)}>
                <div className="animate-pulse">
                    <div className="bg-gray-300 rounded h-4 w-3/4"></div>
                </div>
                <div className="animate-pulse">
                    <div className="bg-gray-300 rounded h-4 w-1/2"></div>
                </div>
                <div className="animate-pulse">
                    <div className="bg-gray-300 rounded h-4 w-5/6"></div>
                </div>
                {text && (
                    <p className="text-sm text-gray-600 animate-pulse text-center mt-4">{text}</p>
                )}
            </div>
        )
    }

    return null
}