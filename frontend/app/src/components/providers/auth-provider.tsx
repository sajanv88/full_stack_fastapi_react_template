import { Gender, Permission, type UserMeResponse } from "@/api";
import { clearAllTokens, clearIsLoggedIn, getAccessToken, getApiClient, getRefreshToken, isLoggedIn, scheduleTokenRefresh, storeTokenSet, userProfileImageUrl } from "@/lib/utils";
import { createContext, useContext, useEffect, useState } from "react"
import { useLocation, useNavigate } from "react-router";
import { toast } from "sonner";


export type UpdateProfileType = {
    firstName: string;
    lastName: string;
    gender: Gender;
    imageUrl: string | null;
}
type AuthProviderState = {
    isLoggedIn: boolean;
    user: UserMeResponse | null;
    can: (action: Permission) => boolean;
    onUpdateProfile: (data: UpdateProfileType) => Promise<void>;
    refreshCurrentUser: () => Promise<void>;
}

const authContext = createContext<AuthProviderState>({
    isLoggedIn: false,
    user: null,
    can: () => false,
    onUpdateProfile: async () => { },
    refreshCurrentUser: async () => { }
});


export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [authState, setAuthState] = useState<AuthProviderState>({
        isLoggedIn: false,
        user: null,
        can: () => false,
        onUpdateProfile: async () => { },
        refreshCurrentUser: async () => { }
    });
    const navigate = useNavigate();
    const { pathname } = useLocation();
    useEffect(() => {
        async function refreshToken() {

            const auth = getApiClient().auth;
            const refreshToken = getRefreshToken()
            clearIsLoggedIn();
            if (!refreshToken) {
                console.error("No refresh token available");
                clearAllTokens();
                navigate("/login");
                return;
            }

            try {
                const authWithRefresh = await auth.refreshTokenApiV1AuthRefreshPost({
                    requestBody: {
                        refresh_token: refreshToken
                    }

                })
                storeTokenSet(authWithRefresh)
                await fetchUser();
            } catch (error) {
                console.error("Failed to refresh token:", error);
                clearAllTokens();
                navigate("/login");
            }
        }
        const fetchUser = async () => {
            const apiClient = getApiClient();
            const auth = apiClient.auth;
            const users = apiClient.users;
            try {
                const user = await auth.readUsersMeApiV1AuthMeGet();
                setAuthState({
                    isLoggedIn: true,
                    user: {
                        ...user, // Todo: Replace this with cloud storage URL once configured in the backend
                        image_url: userProfileImageUrl(user?.image_url),
                    },
                    can: (action: Permission) => {
                        return user?.role?.permissions?.includes(action) ?? false;
                    },
                    onUpdateProfile: async (data: UpdateProfileType) => {
                        try {
                            await users.updateUserApiV1UsersUserIdPut({
                                userId: user.id,
                                requestBody: {
                                    first_name: data.firstName,
                                    last_name: data.lastName,
                                    gender: data.gender,
                                    image_url: data.imageUrl,
                                }
                            })
                            toast.success("Profile updated successfully", {
                                richColors: true
                            });
                            await fetchUser();
                        } catch (error) {
                            console.error("Error updating profile:", error);
                            toast.error("Failed to update profile", {
                                richColors: true
                            });
                        }
                    },
                    refreshCurrentUser: async () => {
                        await fetchUser();
                    }
                });
                if (isLoggedIn()) {
                    return;
                }
                navigate("/dashboard");
            } catch (error) {
                await refreshToken();
            }

        };

        const accessToken = getAccessToken();
        if (pathname !== "/register" && accessToken) {
            fetchUser();
            scheduleTokenRefresh(refreshToken);
        }

    }, []);

    return (
        <authContext.Provider value={authState}>
            {children}
        </authContext.Provider>
    );
}


export function useAuthContext() {
    const context = useContext(authContext);
    if (!context) {
        throw new Error("useAuthContext must be used within an AuthProvider");
    }
    return context;
}
