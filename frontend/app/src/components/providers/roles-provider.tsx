import { CreateRoleDto, RoleListDto, UpdateRoleDto } from '@/api';
import { createContext, useContext, useEffect, useState } from 'react';
import { IResponseData } from '../shared/iresponse-data.inteface';
import { useSearchParams } from 'react-router';
import { toast } from 'sonner';
import { getApiClient } from '@/lib/utils';
import { useAuthContext } from './auth-provider';


export type RoleResponse = RoleListDto
export type RolesType = RoleResponse["roles"][0]
type ActionType = 'edit' | 'delete' | 'clone' | 'manage_permissions'
type Action = {
    type: ActionType;
    role: RolesType;
}

interface RolesProviderState {
    roleResponse: IResponseData<RolesType>;
    refreshRoles: () => void;
    onCreateNewRole: (params: CreateRoleDto) => Promise<void>;
    loading: boolean;
    selectedRole?: Action;
    onSelectRole: (action?: Action) => void;
    onUpdateRole: (roleId: string, params: UpdateRoleDto) => Promise<void>;
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
    onUpdateRole: (roleId: string, params: UpdateRoleDto) => {
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
    const { accessToken } = useAuthContext();
    const [searchParams] = useSearchParams();
    const [pending, setPending] = useState(true);
    const [roleError, setRoleError] = useState<string | null>(null);

    const [roleResponse, setRoleResponse] = useState<IResponseData<RolesType>>(initialState.roleResponse);
    const [selectedRole, setSelectedRole] = useState<Action | undefined>(initialState.selectedRole);
    const apiClient = getApiClient(accessToken);
    const role = apiClient.roles;

    async function fetchRoles() {
        setRoleError(null);
        const skip = searchParams.get("skip");
        const limit = searchParams.get("limit");
        try {
            const res = await role.listRolesApiV1RolesGet({ skip: skip ? parseInt(skip) : 0, limit: limit ? parseInt(limit) : 10 });

            setRoleResponse({
                items: res.roles,
                hasNext: res.hasNext,
                total: res.total,
                hasPrevious: res.hasPrevious,
                limit: res.limit,
                skip: res.skip,
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

    async function onCreateNewRole(params: CreateRoleDto) {
        await role.createRoleApiV1RolesPost({
            requestBody: params
        });
    }

    async function onUpdateRole(role_id: string, params: CreateRoleDto) {
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
                    position: "top-right",
                });
                await refreshRoles();
            } catch (error) {
                console.error("Error cloning role:", error);
                toast.error("Failed to clone role", {
                    richColors: true,
                    position: "top-right",
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
                position: "top-right",
            });
            await refreshRoles();
        } catch (error) {

            toast.error("Failed to delete role", {
                richColors: true,
                description: "Check if the role is assigned to any users",
                position: "top-right",
                duration: 3000,
            });
        }

    }

    useEffect(() => {
        refreshRoles();
    }, [searchParams, accessToken]);

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