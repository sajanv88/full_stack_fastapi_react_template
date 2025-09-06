import { ApiClient, PermissionBase } from "@/api";
import { getAccessToken } from "@/lib/utils";
import { useEffect, useState, useTransition } from "react";
import { CheckIcon, ChevronsUpDownIcon, InfoIcon, XIcon } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from "@/components/ui/command"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";

interface ListPermissionProps {
    value?: string[]
    onChange?: (permissions: string[]) => void
    placeholder?: string
    multiSelect?: boolean
    maxSelections?: number
}

export function ListPermission({
    value = [],
    onChange,
    placeholder = "Select permission...",
    multiSelect = false,
    maxSelections
}: ListPermissionProps) {
    const [permissions, setPermissions] = useState<PermissionBase[]>([]);
    const [pending, startTransition] = useTransition();
    const [error, setError] = useState<string | null>(null);
    const [open, setOpen] = useState(false)
    const [selectedPermissions, setSelectedPermissions] = useState<string[]>(value)

    const accessToken = getAccessToken();
    const apiClient = new ApiClient({
        HEADERS: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
    const permission = apiClient.permissions;
    async function fetchPermissions() {
        try {
            const response = await permission.getPermissionsApiV1PermissionsGet();
            setPermissions(response);
        } catch (error) {
            console.error("Failed to fetch permissions:", error);
            setError("Failed to fetch permissions");
        }
    }

    useEffect(() => {
        startTransition(() => {
            fetchPermissions();
        });
    }, []);



    const handlePermissionSelect = (permissionName: string) => {
        let newSelectedPermissions: string[];

        if (multiSelect) {
            if (selectedPermissions.includes(permissionName)) {
                // Remove permission if already selected
                newSelectedPermissions = selectedPermissions.filter(p => p !== permissionName);
            } else {
                // Add permission if not selected and within limits
                if (maxSelections && selectedPermissions.length >= maxSelections) {
                    return; // Don't add if max selections reached
                }
                newSelectedPermissions = [...selectedPermissions, permissionName];
            }
        } else {
            // Single select mode
            newSelectedPermissions = selectedPermissions.includes(permissionName) ? [] : [permissionName];
            setOpen(false); // Close popover for single select
        }

        setSelectedPermissions(newSelectedPermissions);
        onChange?.(newSelectedPermissions);
    };

    const handleRemovePermission = (permissionName: string) => {
        const newSelectedPermissions = selectedPermissions.filter(p => p !== permissionName);
        setSelectedPermissions(newSelectedPermissions);
        onChange?.(newSelectedPermissions);
    };

    const getDisplayText = () => {
        if (selectedPermissions.length === 0) {
            return placeholder;
        }

        if (selectedPermissions.length === 1) {
            return permissions.find(p => p.name === selectedPermissions[0])?.name || selectedPermissions[0];
        }

        return `${selectedPermissions.length} permissions selected`;
    };


    if (error) {
        return (
            <Alert variant="destructive">
                <InfoIcon className="mr-2 h-4 w-4" />
                <AlertTitle>An error occurred</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
            </Alert>
        )
    }

    return (
        <div className="space-y-2">
            {/* Selected permissions badges (for multi-select) */}
            {multiSelect && selectedPermissions.length > 0 && (
                <div className="flex flex-wrap gap-1">
                    {selectedPermissions.map((permissionName) => {
                        const permission = permissions.find(p => p.name === permissionName);
                        return (
                            <Badge key={permissionName} variant="secondary" className="text-xs">
                                {permission?.name || permissionName}
                                <button
                                    type="button"
                                    className="ml-1 hover:text-destructive  focus:text-destructive rounded-full"
                                    onClick={() => handleRemovePermission(permissionName)}
                                >
                                    ×
                                </button>
                            </Badge>
                        );
                    })}
                </div>
            )}

            <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={open}
                        className="w-full justify-between"
                    >
                        {getDisplayText()}
                        <ChevronsUpDownIcon className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="p-0">
                    <Command>
                        <CommandInput placeholder={pending ? "Loading..." : "Search permission..."} />
                        <CommandList>
                            <CommandEmpty>No permission found.</CommandEmpty>
                            <CommandGroup>
                                {/* Max selections warning */}
                                {multiSelect && maxSelections && selectedPermissions.length >= maxSelections && (
                                    <div className="px-2 py-1 text-xs text-muted-foreground border-b">
                                        Maximum {maxSelections} permissions can be selected
                                    </div>
                                )}

                                {permissions.map((permission) => {
                                    const isSelected = selectedPermissions.includes(permission.name);
                                    const isDisabled = multiSelect && maxSelections ?
                                        selectedPermissions.length >= maxSelections && !isSelected : false;

                                    return (
                                        <CommandItem
                                            key={permission.name}
                                            value={permission.name}
                                            disabled={isDisabled}
                                            onSelect={() => handlePermissionSelect(permission.name)}
                                            className={cn(
                                                "cursor-pointer",
                                                isDisabled && "opacity-50 cursor-not-allowed"
                                            )}
                                        >
                                            <CheckIcon
                                                className={cn(
                                                    "mr-2 h-4 w-4",
                                                    isSelected ? "opacity-100" : "opacity-0"
                                                )}
                                            />
                                            {permission.name}
                                            {isSelected && multiSelect && (
                                                <Badge variant="outline" className="ml-auto text-xs">
                                                    Selected
                                                </Badge>
                                            )}
                                        </CommandItem>
                                    )
                                })}
                            </CommandGroup>
                        </CommandList>
                    </Command>
                </PopoverContent>
            </Popover>
        </div>
    )
}