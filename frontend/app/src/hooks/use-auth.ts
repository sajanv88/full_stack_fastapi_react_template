import { ApiClient, type NewUser } from "@/api";
import { storeTokenSet } from "@/lib/utils";
import { useNavigate } from "react-router";
import { toast } from "sonner";

const auth = new ApiClient().auth

export function useAuth() {
    const navigate = useNavigate()
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
            navigate("/dashboard");
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
            await auth.registerApiV1AuthRegisterPost({
                requestBody: data
            });
            toast.success("Registration successful!", {
                richColors: true
            });
            navigate("/login");
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