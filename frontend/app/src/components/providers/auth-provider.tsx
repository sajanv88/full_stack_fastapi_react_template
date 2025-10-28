import { CreateUserDto, Gender, Permission, type MeResponseDto } from "@/api";
import { useProfileImage } from "@/hooks/use-profile-image";
import {
    getApiClient,
} from "@/lib/utils";
import { createContext, useContext, useEffect, useState, useCallback } from "react"
import { useLocation, useNavigate } from "react-router";
import { toast } from "sonner";

const notProtectedRoutes = ["/password_reset_confirmation", "/password-reset-request", "/register", "/forgot-password", "/magic_link_login"];
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
    register: (data: CreateUserDto) => Promise<any>,
    resendActivationEmail: () => Promise<void>;
}

const authContext = createContext<AuthProviderState>({
    isLoggedIn: false,
    user: null,
    can: () => false,
    onUpdateProfile: async () => { },
    refreshCurrentUser: async () => { },
    accessToken: "",
    login: async () => { },
    register: async () => { },
    resendActivationEmail: async () => { },
});


export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [isLoggedInState, setIsLoggedInState] = useState<boolean>(false);
    const [user, setUser] = useState<MeResponseDto | null>(null);
    const [accessToken, setAccessToken] = useState<string>("");

    const navigate = useNavigate();
    const { pathname } = useLocation();
    const { getProfileImage } = useProfileImage(accessToken);

    const refreshToken = useCallback(async function refreshToken() {
        setIsLoggedInState(false)
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
                imageUrl = await getProfileImage(user.image_url);
            }
            setIsLoggedInState(true);
            setUser({ ...user, image_url: imageUrl });

        } catch (error) {
            await refreshToken();
        }

    }, [accessToken]);


    async function resendActivationEmail() {
        if (!user) return;
        try {
            const auth = getApiClient(accessToken).account;
            await auth.resendActivationEmailApiV1AccountResendActivationEmailPost({
                requestBody: {
                    email: user.email,
                    id: user.id,
                    first_name: user.first_name,
                    tenant_id: user.tenant_id
                }
            });
            toast.success("Activation email resent successfully. Please check your email.", {
                richColors: true,
                position: "top-right"
            });
        } catch (error) {
            console.error("Failed to resend activation email:", error);
            toast.error("Failed to resend activation email", {
                richColors: true,
                position: "top-right"
            });
        }

    }

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
            await auth.registerApiV1AccountRegisterPost({
                requestBody: data
            });

            toast.success("Registration successful! Please check your email to verify your account.", {
                richColors: true,
                position: "top-right",
                description: "Redirecting to login..."
            });
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

    // Todo: Remove this worker implementation

    // useEffect(() => {
    //     const worker = new Worker(new URL('../../worker.ts', import.meta.url));
    //     worker.addEventListener("message", (event: MessageEvent<TokenSetDto | { type: string } | { message: string; code: number }>) => {
    //         console.log("AuthProvider received message from worker:", event.data);
    //         if (event.data && 'access_token' in event.data) {
    //             setAccessToken(event.data.access_token);
    //         } else if (event.data && 'code' in event.data) {
    //             if (event.data.code === 401 || event.data.code === 400) {
    //                 setIsLoggedInState(false);
    //                 setUser(null);
    //                 setAccessToken("");
    //                 navigate("/login");
    //             }
    //         }

    //     });
    //     window.addEventListener("tenant_set", () => {
    //         console.log("tenant_set event received in auth provider");
    //         const tenant = getTenant();
    //         if (tenant) {
    //             worker.postMessage({ tenantId: tenant.id });
    //         }

    //     })

    //     window.addEventListener("tenant_removed", () => {
    //         console.log("tenant_removed event received in auth provider");
    //         worker.postMessage({ tenantId: null });
    //     })

    // }, [])

    useEffect(() => {
        if (notProtectedRoutes.includes(pathname)) {
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
            register,
            resendActivationEmail
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
