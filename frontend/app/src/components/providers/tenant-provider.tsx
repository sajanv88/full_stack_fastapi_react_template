import { TenantListResponse } from '@/api';
import { createContext, useContext, useEffect, useState } from 'react';
import { IResponseData } from '../shared/iresponse-data.inteface';
import { getApiClient } from '@/lib/utils';
import { useSearchParams } from 'react-router';
import { toast } from 'sonner';
import { useAuthContext } from './auth-provider';

export type TenantResponse = TenantListResponse["data"]
export type TenantsType = TenantResponse["tenants"][0]
type ActionType = 'edit' | 'delete'
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
    onSelectTenant: () => { }
}

const TenantsContext = createContext<TenantsProviderState>(initialState);
interface TenantsProviderProps {
    children: React.ReactNode;
}

export function TenantsProvider({ children }: TenantsProviderProps) {
    const [tenantResponse, setTenantResponse] = useState<IResponseData<TenantsType>>(initialState.tenantResponse);
    const [searchParams] = useSearchParams();
    const [selectedTenant, setSelectedTenant] = useState<Action | undefined>(undefined);
    const [pending, setPending] = useState(true);
    const { can } = useAuthContext();
    const isHost = can("host:manage_tenants");

    async function fetchTenants() {
        const skip = searchParams.get("skip");
        const limit = searchParams.get("limit");
        const apiClient = getApiClient();
        try {
            const response = await apiClient.tenants.getTenantsApiV1TenantsGet({ skip: skip ? parseInt(skip) : 0, limit: limit ? parseInt(limit) : 10 });
            setTenantResponse({
                items: response.data.tenants,
                total: response.data.total,
                hasNext: response.data.hasNext,
                hasPrevious: response.data.hasPrevious,
                limit: response.data.limit,
                skip: response.data.skip
            });
        } catch (error) {
            console.error("Failed to fetch tenants", error);
            toast.error("Failed to fetch tenants", {
                richColors: true,
                duration: 5000,
                position: "top-center",
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



    useEffect(() => {
        fetchTenants();
    }, [searchParams]);

    return (
        <TenantsContext.Provider value={{
            tenantResponse,
            refreshTenants,
            isLoading: pending,
            selectedTenant,
            onSelectTenant
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