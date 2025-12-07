import { useState } from "react";
import { Button } from "@/components/ui/button";
import { IconCheck, IconCopy } from "@tabler/icons-react";
import { toast } from "sonner";

export function CopyText({ text }: { text: string }) {
    const [copied, setCopied] = useState<boolean>(false);

    async function handleCopy() {
        try {
            // Check if clipboard API is available
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(text);
            } else {
                // Fallback for older browsers or non-secure contexts
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();

                try {
                    document.execCommand('copy');
                } finally {
                    textArea.remove();
                }
            }

            setCopied(true);
            toast.success("Copied!", { position: "top-right", richColors: true, description: `You must paste the copied redirect URI into your OAuth provider settings.` });
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
            toast.error("Failed to copy!", { position: "top-right", richColors: true });
        }
    }
    return (
        <div
            className="flex items-center justify-between gap-2 group"
        >
            <p className="text-sm font-mono truncate text-muted-foreground flex-1">
                {text}
            </p>
            <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={handleCopy}
            >
                {copied ? (
                    <IconCheck className="h-3 w-3 text-green-500" />
                ) : (
                    <IconCopy className="h-3 w-3" />
                )}
            </Button>
        </div>
    );
}