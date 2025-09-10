
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
    disabled?: boolean;
};

interface TableActionsProps<D> {
    options: ActionOption<D>[];
    resource: 'user' | 'role' | 'tenant';
}
export function TableActions<D>({ options, resource }: TableActionsProps<D>) {
    const { can } = useAuthContext();
    const isAdmin = can("full:access");
    let shouldDisableBtn = !isAdmin;
    if (resource === 'user') {
        const isUserSelfUpdate = can("user:self_read_and_write_only");
        shouldDisableBtn = !isAdmin && !isUserSelfUpdate;
    }
    if (resource === 'role') {
        const isRoleReadAndWrite = can("role:read_and_write_only");
        const isRoleDelete = can("role:delete_only");
        shouldDisableBtn = !isAdmin && !isRoleReadAndWrite && !isRoleDelete;
    }
    if (resource === 'tenant') {
        const isHostManageTenants = can("host:manage_tenants");
        console.log({ isHostManageTenants });
        shouldDisableBtn = !isAdmin && !isHostManageTenants;
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
                        <DropdownMenuItem key={option.label} disabled={!option.disabled} onClick={() => option.onClick(option.data)}>
                            {option.label}
                        </DropdownMenuItem>
                    ))}
                </DropdownMenuGroup>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}