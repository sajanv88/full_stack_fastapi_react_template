import { getApiClient } from "@/lib/utils";
import { useCallback } from "react";


export function useProfileImage(accessToken: string) {
    const fetchImage = useCallback(async function fetchImage(key: string | null | undefined): Promise<string> {
        if (!key) {
            return "https://github.com/evilrabbit.png";
        }
        const apiClient = getApiClient(accessToken).users;
        const response = await apiClient.getProfileImageApiV1UsersProfileImageKeyGet({
            imageKey: key
        });
        return response.image_url
    }, [accessToken]);

    return { getProfileImage: fetchImage };
}