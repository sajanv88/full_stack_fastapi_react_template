import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react"
interface PageHeaderProps {
    title: string;
    subtitle?: string;
    cta?: {
        label: string;
        onClick: () => void;
        disabled?: boolean;
        icon?: React.ReactNode;
    };
}
export function PageHeader({ title, subtitle, cta }: PageHeaderProps) {
    return (
        <header className="flex border-b pb-5 items-center justify-between mb-4">
            <div className="flex flex-col">
                <h1 className="text-2xl font-bold">{title}</h1>
                {subtitle && <h2 className="text-sm text-muted-foreground">{subtitle}</h2>}
            </div>
            {cta && <Button onClick={cta.onClick} disabled={cta.disabled}>
                {cta.icon ? <>{cta.icon}</> : <Plus className="w-4 h-4" />}
                {cta.label}
            </Button>
            }
        </header>
    );
}