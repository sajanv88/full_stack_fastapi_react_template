
import { Button } from "@/components/ui/button"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { CogIcon } from 'lucide-react'
import { useAuthContext } from "@/components/providers/auth-provider";

export type ActionOption<D> = {
    label: string;
    data: D;
    onClick: (value: D) => void;
};

interface TableActionsProps<D> {
    options: ActionOption<D>[];
    resource: 'user' | 'role';
}
export function TableActions<D>({ options, resource }: TableActionsProps<D>) {
    const { can } = useAuthContext();
    const isAdmin = can("full:access");
    let shouldDisableBtn = !isAdmin;
    if (resource === 'user') {
        const isUserSelfUpdate = can("user:self_read_and_write_only");
        shouldDisableBtn = !isAdmin && !isUserSelfUpdate;
    }
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button disabled={shouldDisableBtn}>
                    <CogIcon className="h-4 w-4" />
                    Actions
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-56">
                <DropdownMenuGroup>
                    {options.map((option) => (
                        <DropdownMenuItem key={option.label} onClick={() => option.onClick(option.data)}>
                            {option.label}
                        </DropdownMenuItem>
                    ))}
                </DropdownMenuGroup>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}