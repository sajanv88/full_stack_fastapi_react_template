import { RoleDto } from "@/api";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { getApiClient } from "@/lib/utils";
import { useState, useEffect } from "react";
import { Search, Users, CheckCircle } from "lucide-react";
import { toast } from "sonner";
import { useAuthContext } from "../providers/auth-provider";


interface ManageUserRolesProps {
    open: boolean;
    onDismiss: () => void;
    userId: string;
}
export function ManageUserRoles({ open, onDismiss, userId }: ManageUserRolesProps) {
    const [roles, setRoles] = useState<RoleDto[]>([]);
    const [query, setQuery] = useState("");
    const [selectedRole, setSelectedRole] = useState<RoleDto | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isSearching, setIsSearching] = useState(false);
    const { accessToken } = useAuthContext();
    const apiClient = getApiClient(accessToken);


    async function fetchRoles() {
        if (!query.trim()) {
            setRoles([]);
            return;
        }

        setIsSearching(true);
        try {
            const roles = await apiClient.roles.searchRoleByNameApiV1RolesSearchByNameGet({
                name: query
            });
            setRoles(roles);
        } catch (error) {
            console.error('Failed to fetch roles:', error);
            setRoles([]);
        } finally {
            setIsSearching(false);
        }
    }

    const handleSearch = () => {
        fetchRoles();
    };

    const handleRoleSelect = (role: RoleDto) => {
        setSelectedRole(role);
    };

    const handleAssignRole = async () => {
        if (!selectedRole) return;

        setIsLoading(true);
        try {
            // Add your role assignment logic here
            await apiClient.users.patchUserApiV1UsersUserIdAssignRolePatch({
                userId: userId,
                requestBody: {
                    role_id: selectedRole.id
                }
            });
            toast.success("Role assigned successfully", { richColors: true, position: "top-right" });
            onDismiss();
        } catch (error) {
            console.error('Failed to assign role:', error);
            toast.error("Failed to assign role", { richColors: true, position: "top-right" });
        } finally {
            setIsLoading(false);
        }
    };

    // Search on Enter key press
    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    // Reset state when dialog closes
    useEffect(() => {
        if (!open) {
            setQuery("");
            setRoles([]);
            setSelectedRole(null);
        }
    }, [open]);

    return (
        <Dialog open={open} onOpenChange={onDismiss} modal>
            <DialogContent>
                <DialogTitle className="text-lg font-medium leading-6 mb-2">
                    Manage User Roles
                </DialogTitle>
                <DialogDescription className="text-sm mb-4">
                    Search and assign roles to the selected user.
                </DialogDescription>

                <div className="space-y-4">
                    {/* Search Input */}
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                        <Input
                            type="text"
                            placeholder="Search roles by name..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyUp={handleKeyPress}
                            className="pl-10 pr-20"
                        />
                        <Button
                            onClick={handleSearch}
                            disabled={!query.trim() || isSearching}
                            size="sm"
                            className="absolute right-1 top-1/2 transform -translate-y-1/2"
                        >
                            {isSearching ? 'Searching...' : 'Search'}
                        </Button>
                    </div>

                    <Separator />

                    {/* Search Results */}
                    <div className="max-h-64 overflow-y-auto">
                        {query && roles.length === 0 && !isSearching && (
                            <div className="text-center py-8 text-gray-500">
                                <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
                                <p className="text-sm">No roles found for "{query}"</p>
                            </div>
                        )}

                        {!query && (
                            <div className="text-center py-8 text-gray-500">
                                <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
                                <p className="text-sm">Enter a role name to search</p>
                            </div>
                        )}

                        {roles.length > 0 && (
                            <div className="space-y-2 px-3 pb-3">
                                <p className="text-sm font-medium">
                                    Found {roles.length} role{roles.length !== 1 ? 's' : ''}:
                                </p>
                                {roles.map((role) => (
                                    <Card
                                        key={role.id}
                                        className={`px-3 cursor-pointer transition-all hover:shadow-md ${selectedRole?.id === role.id
                                            ? 'ring-1 ring-primary bg-primary/5'
                                            : 'hover:bg-primary/10'
                                            }`}
                                        onClick={() => handleRoleSelect(role)}
                                    >
                                        <CardContent className="p-1">
                                            <div className="flex items-center justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center space-x-2">
                                                        <h4 className="font-medium text-sm">{role.name}</h4>
                                                        {selectedRole?.id === role.id && (
                                                            <CheckCircle className="h-4 w-4 text-primary" />
                                                        )}
                                                    </div>
                                                    {role.description && (
                                                        <p className="text-xs  mt-1">
                                                            {role.description}
                                                        </p>
                                                    )}
                                                </div>
                                                <Badge variant="outline" className="text-xs">
                                                    Role
                                                </Badge>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Action Buttons */}
                    {selectedRole && (
                        <>
                            <Separator />
                            <div className="p-3 rounded-lg">
                                <p className="text-sm font-medium  mb-1">Selected Role:</p>
                                <div className="flex items-center justify-between">
                                    <span className="text-sm">{selectedRole.name}</span>
                                    <Badge variant="default" className="text-xs">
                                        Selected
                                    </Badge>
                                </div>
                            </div>
                        </>
                    )}

                    <div className="flex justify-end space-x-2 pt-4">
                        <Button
                            variant="outline"
                            onClick={onDismiss}
                            disabled={isLoading}
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={handleAssignRole}
                            disabled={!selectedRole || isLoading}
                        >
                            {isLoading ? 'Assigning...' : 'Assign Role'}
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    )
}