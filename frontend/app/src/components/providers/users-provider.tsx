import { ApiClient, NewUser, UserListResponse, UserUpdate } from '@/api';
import { createContext, useContext, useEffect, useState, useTransition } from 'react';
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
    createNewUser: (params: NewUser) => Promise<void>;
    loading: boolean;
    selectedUser?: Action;
    selectUser: (action?: Action) => void;
    updateUser: (userId: string, params: UserUpdate) => Promise<void>;
    onDeleteUser: () => Promise<void>;
}

const initialState: UsersProviderState = {
    refreshUsers: () => { },
    createNewUser: async () => { },
    loading: true,
    userResponse: {
        items: [],
        total: 0,
        hasNext: false,
        hasPrevious: false,
        limit: 0,
        skip: 0
    },
    selectedUser: undefined,
    onDeleteUser: () => Promise.resolve(),
    updateUser: (userId: string, params: UserUpdate) => {
        console.debug("Updating user:", userId, params);
        return Promise.resolve();
    },
    selectUser: () => { }
}

const UsersContext = createContext<UsersProviderState>(initialState);

interface UsersProviderProps {
    children: React.ReactNode;
}

export function UsersProvider({ children }: UsersProviderProps) {
    const [searchParams] = useSearchParams();
    const [pending, startTransition] = useTransition();

    const [userResponse, setUserResponse] = useState<IResponseData<UsersType>>(initialState.userResponse);
    const [selectedUser, setSelectedUser] = useState<Action | undefined>(initialState.selectedUser);
    const accessToken = getAccessToken();
    const user = new ApiClient({
        HEADERS: {
            Authorization: `Bearer ${accessToken}`,
        },
    }).users;

    async function fetchUsers() {

        const skip = searchParams.get("skip");
        const limit = searchParams.get("limit");
        const users = await user.getUsersApiV1UsersGet({ skip: skip ? parseInt(skip) : 0, limit: limit ? parseInt(limit) : 10 });
        setUserResponse({
            items: users.data.users,
            hasNext: users.data.hasNext,
            total: users.data.total,
            hasPrevious: users.data.hasPrevious,
            limit: users.data.limit,
            skip: users.data.skip,
        });
    }

    async function refreshUsers() {
        startTransition(() => {
            fetchUsers();
        });
    }

    async function createNewUser(params: NewUser) {
        await user.createUserApiV1UsersPost({
            requestBody: params
        });
    }

    async function updateUser(user_id: string, params: UserUpdate) {
        await user.updateUserApiV1UsersUserIdPut({
            userId: user_id,
            requestBody: {
                first_name: params.first_name,
                last_name: params.last_name,
                gender: params.gender
            }
        });
    }

    function selectUser(action?: Action) {
        if (action?.type === 'resend_email') {
            toast.success("User email resent successfully", {
                richColors: true,
                position: "top-center",
            });
        }
        setSelectedUser(action);

    }

    async function onDeleteUser() {
        if (!selectedUser) return;
        await user.deleteUserApiV1UsersUserIdDelete({
            userId: selectedUser.user.id
        });
        selectUser(undefined);
        toast.success("User deleted successfully", {
            richColors: true,
            position: "top-center",
        });
    }

    useEffect(() => {
        startTransition(() => {
            fetchUsers();
        });
    }, [searchParams]);

    return (
        <UsersContext.Provider value={
            {
                userResponse,
                selectedUser,
                refreshUsers,
                createNewUser,
                selectUser,
                loading: pending,
                updateUser,
                onDeleteUser
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