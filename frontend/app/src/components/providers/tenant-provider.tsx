import { CreateTenantDto, TenantListDto, UpdateTenantDto } from '@/api';
import { createContext, useContext, useEffect, useState } from 'react';
import { IResponseData } from '../shared/iresponse-data.inteface';
import { getApiClient } from '@/lib/utils';
import { useSearchParams } from 'react-router';
import { toast } from 'sonner';
import { useAuthContext } from './auth-provider';

export type TenantResponse = TenantListDto
export type TenantsType = TenantResponse["tenants"][0]
type ActionType = 'edit' | 'delete' | 'manage_features';
type Action = {
    type: ActionType;
    tenant: TenantsType;
}


interface TenantsProviderState {
    tenantResponse: IResponseData<TenantsType>;
    refreshTenants: () => void;
    isLoading: boolean;
    selectedTenant?: Action;
    onSelectTenant: (action?: Action) => void;
    onCreateNewTenant: (newTenant: CreateTenantDto) => Promise<void>;
    onDeleteTenant: () => Promise<void>;
    onUpdateTenant: (tenantId: string, updatedTenant: UpdateTenantDto) => Promise<void>;

}

const initialState: TenantsProviderState = {
    tenantResponse: {
        items: [],
        total: 0,
        hasNext: false,
        hasPrevious: false,
        limit: 0,
        skip: 0
    },
    refreshTenants: () => { },
    isLoading: true,
    selectedTenant: undefined,
    onSelectTenant: () => { },
    onCreateNewTenant: async () => { },
    onDeleteTenant: async () => { },
    onUpdateTenant: async () => { },
}

const TenantsContext = createContext<TenantsProviderState>(initialState);
interface TenantsProviderProps {
    children: React.ReactNode;
}

export function TenantsProvider({ children }: TenantsProviderProps) {
    const { accessToken, can } = useAuthContext();
    const [tenantResponse, setTenantResponse] = useState<IResponseData<TenantsType>>(initialState.tenantResponse);
    const [searchParams] = useSearchParams();
    const [selectedTenant, setSelectedTenant] = useState<Action | undefined>(undefined);
    const [pending, setPending] = useState(true);
    const isHost = can("host:manage_tenants");
    const apiClient = getApiClient(accessToken);

    async function fetchTenants() {
        toast.dismiss();
        const skip = searchParams.get("skip");
        const limit = searchParams.get("limit");
        try {
            const response = await apiClient.tenants.listTenantsApiV1TenantsGet({ skip: skip ? parseInt(skip) : 0, limit: limit ? parseInt(limit) : 10 });
            setTenantResponse({
                items: response.tenants,
                total: response.total,
                hasNext: response.hasNext,
                hasPrevious: response.hasPrevious,
                limit: response.limit,
                skip: response.skip
            });
        } catch (error) {
            console.error("Failed to fetch tenants", error);
            toast.error("Failed to fetch tenants", {
                richColors: true,
                duration: 5000,
                position: "top-right",
                description: !isHost ? "You do not have permission to view this resource." : undefined
            });
        } finally {
            setPending(false);
        }
    }


    const refreshTenants = async () => {
        setPending(true);
        await fetchTenants();
    }

    const onSelectTenant = (action?: Action) => {
        setSelectedTenant(action);
    }

    async function onUpdateTenant(tenantId: string, updatedTenant: UpdateTenantDto) {
        try {
            await apiClient.tenants.updateTenantApiV1TenantsTenantIdPut({
                tenantId,
                requestBody: updatedTenant
            });
            toast.success("Tenant updated successfully", {
                richColors: true,
                position: "top-right"
            });
            await fetchTenants();
        } catch (error) {
            console.error("Failed to update tenant", error);
            toast.error("Failed to update tenant", {
                richColors: true,
                position: "top-right"
            });
        }
    }

    const onCreateNewTenant = async (newTenant: CreateTenantDto) => {
        try {
            await apiClient.tenants.createTenantApiV1TenantsPost({
                requestBody: newTenant
            });
            toast.success("Tenant created successfully", {
                richColors: true,
                position: "top-right"
            });
            await fetchTenants();
        } catch (error) {
            console.error("Failed to create tenant", error);
            toast.error("Failed to create tenant", {
                richColors: true,
                position: "top-right"
            });
        }
    }

    const onDeleteTenant = async () => {
        if (!selectedTenant) return;
        try {
            await apiClient.tenants.deleteTenantApiV1TenantsIdDelete({
                id: selectedTenant.tenant.id!
            });
            toast.success("Tenant deleted successfully", {
                richColors: true,
                position: "top-right"
            });
            setSelectedTenant(undefined);
            await fetchTenants();
        } catch (error) {
            console.error("Failed to delete tenant", error);
            toast.error("Failed to delete tenant", {
                richColors: true,
                position: "top-right"
            });
        }
    }

    useEffect(() => {
        fetchTenants();
    }, [searchParams, accessToken]);



    return (
        <TenantsContext.Provider value={{
            tenantResponse,
            refreshTenants,
            isLoading: pending,
            selectedTenant,
            onSelectTenant,
            onCreateNewTenant,
            onDeleteTenant,
            onUpdateTenant
        }}>
            {children}
        </TenantsContext.Provider>
    )
}

export function useTenants() {
    const context = useContext(TenantsContext);
    if (!context) {
        throw new Error("useTenants must be used within a TenantsProvider");
    }
    return context;
}