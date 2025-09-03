import { ApiClient, type UserMeResponse } from "@/api";
import { clearAllTokens, clearIsLoggedIn, getAccessToken, getRefreshToken, isLoggedIn, storeTokenSet } from "@/lib/utils";
import { createContext, useContext, useEffect, useState } from "react"
import { useNavigate } from "react-router";


type AuthProviderState = {
    isLoggedIn: boolean;
    user: UserMeResponse | null;
}

const authContext = createContext<AuthProviderState>({
    isLoggedIn: false,
    user: null
});


export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [authState, setAuthState] = useState<AuthProviderState>({
        isLoggedIn: false,
        user: null
    });
    const navigate = useNavigate();
    useEffect(() => {
        const fetchUser = async () => {
            const accessToken = getAccessToken()
            const auth = new ApiClient({
                HEADERS: {
                    "Authorization": `Bearer ${accessToken}`
                }
            }).auth;
            try {
                const user = await auth.readUsersMeApiV1AuthMeGet();
                setAuthState({
                    isLoggedIn: true,
                    user
                });
                if (isLoggedIn()) {
                    return;
                }
                navigate("/dashboard");
            } catch (error) {
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

        };
        fetchUser();
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
