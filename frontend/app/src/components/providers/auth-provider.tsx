import { CreateUserDto, Gender, Permission, type MeResponseDto } from "@/api";
import { getUserImageUrl } from "@/lib/image-utils";
import {
    getApiClient,
    setTenant,
} from "@/lib/utils";
import { createContext, useContext, useEffect, useState, useCallback } from "react"
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
    user: MeResponseDto | null;
    can: (action: Permission) => boolean;
    onUpdateProfile: (data: UpdateProfileType) => Promise<void>;
    refreshCurrentUser: () => Promise<void>;
    accessToken: string,
    login: (data: { email: string; password: string }) => Promise<void>
    register: (data: CreateUserDto) => Promise<any>
}

const authContext = createContext<AuthProviderState>({
    isLoggedIn: false,
    user: null,
    can: () => false,
    onUpdateProfile: async () => { },
    refreshCurrentUser: async () => { },
    accessToken: "",
    login: async () => { },
    register: async () => { }
});


export function AuthProvider({ children }: { children: React.ReactNode }) {

    const [isLoggedInState, setIsLoggedInState] = useState<boolean>(false);
    const [user, setUser] = useState<MeResponseDto | null>(null);
    const [accessToken, setAccessToken] = useState<string>("");

    const navigate = useNavigate();
    const { pathname } = useLocation();

    const refreshToken = useCallback(async function refreshToken() {
        const auth = getApiClient().account;
        try {
            const authWithRefresh = await auth.refreshTokenApiV1AccountRefreshPost({})
            setAccessToken(authWithRefresh.access_token)

        } catch (error) {
            console.error("Failed to refresh token:", error);
            navigate("/login");
        }
    }, []);

    const fetchUser = useCallback(async function fetchUser() {
        const apiClient = getApiClient(accessToken);
        const auth = apiClient.account;
        try {
            const user = await auth.readUsersMeApiV1AccountMeGet();
            let imageUrl = user.image_url
            if (user.image_url) {
                imageUrl = await getUserImageUrl(user.image_url);
            }
            setIsLoggedInState(true);
            setUser({ ...user, image_url: imageUrl });

        } catch (error) {
            await refreshToken();
        }

    }, [accessToken]);

    function can(action: Permission) {
        return user?.role?.permissions?.includes(action) ?? false;
    }

    async function onUpdateProfile(data: UpdateProfileType) {
        if (!user) return
        try {
            const apiClient = getApiClient(accessToken);
            const users = apiClient.users;
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
    }

    async function refreshCurrentUser() {
        await fetchUser();
    }

    async function login(data: { email: string; password: string }) {
        const auth = getApiClient().account

        try {
            const result = await auth.loginApiV1AccountLoginPost({
                formData: {
                    username: data.email,
                    password: data.password
                }
            });
            toast.success("Login successful!", {
                richColors: true
            });
            setAccessToken(result.access_token)
            await fetchUser()
            navigate('/dashboard');

        } catch (e) {
            if (e instanceof Error) {
                throw e;
            } else {
                throw new Error("An unknown error occurred");
            }
        }
    }

    async function register(data: CreateUserDto) {
        const auth = getApiClient().account

        try {
            const response = await auth.registerApiV1AccountRegisterPost({
                requestBody: data
            });

            if (response.new_tenant_created && response.tenant) {
                setTenant(response.tenant);

            }
            setTimeout(() => {
                navigate("/login");
            }, 2000);
        } catch (e) {
            if (e instanceof Error) {
                throw e;
            } else {
                throw new Error("An unknown error occurred");
            }
        }
    }

    useEffect(() => {
        if (pathname === "/password_reset_confirmation" || pathname === "/password-reset-request") {
            return;
        }
        if (!accessToken) {
            fetchUser();
        } else if (accessToken) {
            fetchUser().then(() => {
                // navigate("/dashboard");
            });

        }

    }, [accessToken]);



    return (
        <authContext.Provider value={{
            isLoggedIn: isLoggedInState,
            accessToken,
            user,
            can,
            onUpdateProfile,
            refreshCurrentUser,
            login,
            register
        }}>
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
