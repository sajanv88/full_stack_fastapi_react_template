import { CreateUserDto, UserListDto, UpdateUserDto } from '@/api';
import { createContext, useContext, useEffect, useState } from 'react';
import { IResponseData } from '../shared/iresponse-data.inteface';
import { getApiClient } from '@/lib/utils';
import { useSearchParams } from 'react-router';
import { toast } from 'sonner';

export type UserResponse = UserListDto
export type UsersType = UserResponse["users"][0]
type ActionType = 'edit' | 'delete' | 'resend_email' | 'manage_roles';
type Action = {
    type: ActionType;
    user: UsersType;
}

interface UsersProviderState {
    userResponse: IResponseData<UsersType>;
    refreshUsers: () => void;
    onCreateNewUser: (params: CreateUserDto) => Promise<void>;
    loading: boolean;
    selectedUser?: Action;
    onSelectUser: (action?: Action) => void;
    onUpdateUser: (userId: string, params: UpdateUserDto) => Promise<void>;
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
    onUpdateUser: (userId: string, params: UpdateUserDto) => {
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
    const apiClient = getApiClient();
    const user = apiClient.users;
    const auth = apiClient.account;

    async function fetchUsers() {

        const skip = searchParams.get("skip");
        const limit = searchParams.get("limit");
        try {
            const res = await user.listUsersApiV1UsersGet({ skip: skip ? parseInt(skip) : 0, limit: limit ? parseInt(limit) : 10 });
            setUserResponse({
                items: res.users,
                hasNext: res.hasNext,
                total: res.total,
                hasPrevious: res.hasPrevious,
                limit: res.limit,
                skip: res.skip,
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

    async function onCreateNewUser(params: CreateUserDto) {
        await user.createUserApiV1UsersPost({
            requestBody: params
        });
    }

    async function onUpdateUser(user_id: string, params: UpdateUserDto) {
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
                await auth.resendActivationEmailApiV1AccountResendActivationEmailPost({
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