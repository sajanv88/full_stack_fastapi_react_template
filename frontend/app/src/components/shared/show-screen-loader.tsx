import { Loading } from "./loading";

interface ShowScreenLoaderProps {
    message?: string;
}
export function ShowScreenLoader({ message }: ShowScreenLoaderProps) {
    return (
        <div className="flex items-center justify-center min-h-[400px]">
            <div className="flex flex-col items-center gap-4">
                <Loading variant="dots" />
                <p className="text-sm text-muted-foreground">{message || "Loading..."}</p>
            </div>
        </div>
    )
}