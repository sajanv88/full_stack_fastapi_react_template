import { type NewUser } from "@/api";
import { getApiClient, setTenant, storeTokenSet } from "@/lib/utils";
import { toast } from "sonner";



export function useAuth() {
    const auth = getApiClient().auth
    async function login(data: { email: string; password: string }) {
        try {
            const result = await auth.loginApiV1AuthLoginPost({
                formData: {
                    username: data.email,
                    password: data.password
                }
            });
            storeTokenSet(result);
            toast.success("Login successful!", {
                richColors: true
            });
            window.location.href = "/dashboard";
        } catch (e) {
            if (e instanceof Error) {
                throw e;
            } else {
                throw new Error("An unknown error occurred");
            }
        }
    }

    async function register(data: NewUser) {
        try {
            const response = await auth.registerApiV1AuthRegisterPost({
                requestBody: data
            });

            if (response.new_tenant_created && response.tenant) {
                setTenant(response.tenant);
                
            }
            setTimeout(() => {
                window.location.href = "/login";
            }, 2000);
        } catch (e) {
            if (e instanceof Error) {
                throw e;
            } else {
                throw new Error("An unknown error occurred");
            }
        }
    }

    return {
        login,
        register
    }
}