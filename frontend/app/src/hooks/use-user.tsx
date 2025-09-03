import { ApiClient, type UserListResponse } from "@/api";
import { getAccessToken } from "@/lib/utils";
import { useEffect, useState, useTransition } from "react";
import { useLocation } from 'react-router';
export function useUser() {
    const { search } = useLocation();
    const [pending, startTransition] = useTransition();
    const [userResponse, setUserResponse] = useState<UserListResponse>();
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
            console.log(`Fetching users with skip: ${skip}, limit: ${limit}`);
            const users = await user.getUsersApiV1UsersGet({ skip: skip ? parseInt(skip) : 0, limit: limit ? parseInt(limit) : 10 });

            console.log(users);
            setUserResponse(users);
        }


        startTransition(() => {
            fetchUsers();
        });
    }, []);



    return { userResponse, loading: pending };
}