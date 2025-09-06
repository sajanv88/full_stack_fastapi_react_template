import { ApiClient, NewUser, UserListResponse, UserUpdate } from '@/api';
import { createContext, useContext, useEffect, useState } from 'react';
import { IResponseData } from '../shared/iresponse-data.inteface';
import { getAccessToken } from '@/lib/utils';
import { useSearchParams } from 'react-router';
import { toast } from 'sonner';

export type UserResponse = UserListResponse["data"]
export type UsersType = UserResponse["users"][0]
type ActionType = 'edit' | 'delete' | 'resend_email'
type Action = {
    type: ActionType;
    user: UsersType;
}

interface UsersProviderState {
    userResponse: IResponseData<UsersType>;
    refreshUsers: () => void;
    onCreateNewUser: (params: NewUser) => Promise<void>;
    loading: boolean;
    selectedUser?: Action;
    onSelectUser: (action?: Action) => void;
    onUpdateUser: (userId: string, params: UserUpdate) => Promise<void>;
    onDeleteUser: () => Promise<void>;
    userError: string | null;
}

const initialState: UsersProviderState = {
    refreshUsers: () => { },
    onCreateNewUser: async () => { },
    loading: true,
    userResponse: {
        items: [],
        total: 0,
        hasNext: false,
        hasPrevious: false,
        limit: 0,
        skip: 0
    },
    userError: null,
    selectedUser: undefined,
    onDeleteUser: () => Promise.resolve(),
    onUpdateUser: (userId: string, params: UserUpdate) => {
        console.debug("Updating user:", userId, params);
        return Promise.resolve();
    },
    onSelectUser: () => { }
}

const UsersContext = createContext<UsersProviderState>(initialState);

interface UsersProviderProps {
    children: React.ReactNode;
}

export function UsersProvider({ children }: UsersProviderProps) {
    const [searchParams] = useSearchParams();
    const [pending, setPending] = useState(true);
    const [userError, setUserError] = useState<string | null>(null);
    const [userResponse, setUserResponse] = useState<IResponseData<UsersType>>(initialState.userResponse);
    const [selectedUser, setSelectedUser] = useState<Action | undefined>(initialState.selectedUser);
    const accessToken = getAccessToken();
    const apiClient = new ApiClient({
        HEADERS: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
    const user = apiClient.users;
    const auth = apiClient.auth;

    async function fetchUsers() {

        const skip = searchParams.get("skip");
        const limit = searchParams.get("limit");
        try {
            const users = await user.getUsersApiV1UsersGet({ skip: skip ? parseInt(skip) : 0, limit: limit ? parseInt(limit) : 10 });
            setUserResponse({
                items: users.data.users,
                hasNext: users.data.hasNext,
                total: users.data.total,
                hasPrevious: users.data.hasPrevious,
                limit: users.data.limit,
                skip: users.data.skip,
            });
        } catch (error) {
            console.error("Failed to fetch users:", error);
            if (error instanceof Error) {
                setUserError(error.message);
            } else {
                setUserError("Failed to fetch users");
            }
        }

    }

    async function refreshUsers() {
        setPending(true);
        await fetchUsers();
        setPending(false);
    }

    async function onCreateNewUser(params: NewUser) {
        await user.createUserApiV1UsersPost({
            requestBody: params
        });
    }

    async function onUpdateUser(user_id: string, params: UserUpdate) {
        await user.updateUserApiV1UsersUserIdPut({
            userId: user_id,
            requestBody: {
                first_name: params.first_name,
                last_name: params.last_name,
                gender: params.gender
            }
        });
    }

    async function onSelectUser(action?: Action) {
        if (action?.type === 'resend_email') {
            try {
                await auth.resendActivationEmailApiV1AuthResendActivationEmailPost({
                    requestBody: {
                        email: action.user.email,
                        id: action.user.id,
                        first_name: action.user.first_name
                    }
                });
                toast.success("User email resent successfully", {
                    richColors: true,
                    position: "top-center",
                });
            } catch (e) {
                console.error("Failed to resend user email", e);
                toast.error("Failed to resend user email", {
                    richColors: true,
                    position: "top-center",
                });
            }
            return;
        }
        setSelectedUser(action);

    }

    async function onDeleteUser() {
        if (!selectedUser) return;
        try {
            await user.deleteUserApiV1UsersUserIdDelete({
                userId: selectedUser.user.id
            });
            onSelectUser(undefined);
            toast.success("User deleted successfully", {
                richColors: true,
                position: "top-center",
            });
            await refreshUsers();
        } catch (error) {
            console.error("Error deleting user:", error);
            toast.error("Failed to delete user", {
                richColors: true,
                position: "top-center",
            });
        }
    }

    useEffect(() => {
        refreshUsers();
    }, [searchParams]);

    return (
        <UsersContext.Provider value={
            {
                userResponse,
                selectedUser,
                refreshUsers,
                onCreateNewUser,
                onSelectUser,
                loading: pending,
                onUpdateUser,
                onDeleteUser,
                userError
            }}>
            {children}
        </UsersContext.Provider>
    );
}

export function useUsers() {
    const context = useContext(UsersContext);
    if (!context) {
        throw new Error("useUsers must be used within a UsersProvider");
    }
    return context;
}