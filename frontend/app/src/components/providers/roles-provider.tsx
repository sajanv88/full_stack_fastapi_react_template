import { ApiClient, NewRole, RoleListResponse } from '@/api';
import { createContext, useContext, useEffect, useState, useTransition } from 'react';
import { IResponseData } from '../shared/iresponse-data.inteface';
import { getAccessToken } from '@/lib/utils';
import { useSearchParams } from 'react-router';
import { toast } from 'sonner';


export type RoleResponse = RoleListResponse["data"]
export type RolesType = RoleResponse["roles"][0]
type ActionType = 'edit' | 'delete' | 'clone' | 'manage_permissions'
type Action = {
    type: ActionType;
    role: RolesType;
}

interface RolesProviderState {
    roleResponse: IResponseData<RolesType>;
    refreshRoles: () => void;
    onCreateNewRole: (params: NewRole) => Promise<void>;
    loading: boolean;
    selectedRole?: Action;
    onSelectRole: (action?: Action) => void;
    onUpdateRole: (roleId: string, params: NewRole) => Promise<void>;
    onDeleteRole: () => Promise<void>;
    error: string | null
}

const initialState: RolesProviderState = {
    refreshRoles: () => { },
    onCreateNewRole: async () => { },
    loading: true,
    roleResponse: {
        items: [],
        total: 0,
        hasNext: false,
        hasPrevious: false,
        limit: 0,
        skip: 0
    },
    selectedRole: undefined,
    onDeleteRole: () => Promise.resolve(),
    onUpdateRole: (roleId: string, params: NewRole) => {
        console.debug("Updating role:", roleId, params);
        return Promise.resolve();
    },
    onSelectRole: () => { },
    error: null
}

const RolesContext = createContext<RolesProviderState>(initialState);

interface RolesProviderProps {
    children: React.ReactNode;
}
export function RolesProvider({ children }: RolesProviderProps) {
    const [searchParams] = useSearchParams();
    const [pending, setPending] = useState(true);
    const [roleError, setRoleError] = useState<string | null>(null);

    const [roleResponse, setRoleResponse] = useState<IResponseData<RolesType>>(initialState.roleResponse);
    const [selectedRole, setSelectedRole] = useState<Action | undefined>(initialState.selectedRole);
    const accessToken = getAccessToken();
    const apiClient = new ApiClient({
        HEADERS: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
    const role = apiClient.roles;

    async function fetchRoles() {

        const skip = searchParams.get("skip");
        const limit = searchParams.get("limit");
        try {
            const roles = await role.getRolesApiV1RolesGet({ skip: skip ? parseInt(skip) : 0, limit: limit ? parseInt(limit) : 10 });
            setRoleResponse({
                items: roles.data.roles,
                hasNext: roles.data.hasNext,
                total: roles.data.total,
                hasPrevious: roles.data.hasPrevious,
                limit: roles.data.limit,
                skip: roles.data.skip,
            });
        } catch (error) {
            console.error("Error fetching roles:", error);
            if (error instanceof Error) {
                setRoleError(error.message);
            } else {
                setRoleError("Failed to fetch roles");
            }

        }

    }

    async function refreshRoles() {
        setPending(true);
        await fetchRoles();
        setPending(false);
    }

    async function onCreateNewRole(params: NewRole) {
        await role.createRoleApiV1RolesPost({
            requestBody: params
        });
    }

    async function onUpdateRole(role_id: string, params: NewRole) {
        await role.updateRoleApiV1RolesRoleIdPut({
            roleId: role_id,
            requestBody: params
        });
    }

    async function onSelectRole(action?: Action) {
        if (action?.type === 'clone') {
            try {
                await onCreateNewRole({
                    name: `${action.role.name} copy(${roleResponse.total + 1})`,
                    description: action.role.description
                });
                toast.success("Role cloned successfully", {
                    richColors: true,
                    position: "top-center",
                });
                await refreshRoles();
            } catch (error) {
                console.error("Error cloning role:", error);
                toast.error("Failed to clone role", {
                    richColors: true,
                    position: "top-center",
                });
            }
            return;
        }
        setSelectedRole(action);

    }

    async function onDeleteRole() {
        if (!selectedRole) return;
        try {
            await role.deleteRoleApiV1RolesRoleIdDelete({
                roleId: selectedRole.role.id
            });
            onSelectRole(undefined);
            toast.success("Role deleted successfully", {
                richColors: true,
                position: "top-center",
            });
            await refreshRoles();
        } catch (error) {
            console.error("Error deleting role:", error);
            toast.error("Failed to delete role", {
                richColors: true,
                position: "top-center",
            });
        }

    }

    useEffect(() => {
        refreshRoles();
    }, [searchParams]);

    return (
        <RolesContext.Provider value={
            {
                roleResponse,
                selectedRole,
                refreshRoles,
                onCreateNewRole,
                onSelectRole,
                loading: pending,
                onUpdateRole,
                onDeleteRole,
                error: roleError
            }}>
            {children}
        </RolesContext.Provider>
    );
}

export function useRoles() {
    const context = useContext(RolesContext);
    if (!context) {
        throw new Error("useRoles must be used within a RolesProvider");
    }
    return context;
}