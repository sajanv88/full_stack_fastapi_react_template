import { ApiClient, type UserListResponse } from "@/api";
import { IResponseData } from "@/components/shared/iresponse-data.inteface";
import { getAccessToken } from "@/lib/utils";
import { useEffect, useState, useTransition } from "react";
import { useLocation } from 'react-router';

export type UserResponse = UserListResponse["data"]
export type UsersType = UserResponse["users"][0]

export function useUser() {
    const { search } = useLocation();
    const [pending, startTransition] = useTransition();
    const [userResponse, setUserResponse] = useState<IResponseData<UsersType>>();
    const accessToken = getAccessToken();
    const user = new ApiClient({
        HEADERS: {
            Authorization: `Bearer ${accessToken}`,
        },
    }).users;

    const searchParams = new URLSearchParams(search);

    useEffect(() => {
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


        startTransition(() => {
            fetchUsers();
        });
    }, [searchParams.toString()]);



    return { userResponse, loading: pending };
}