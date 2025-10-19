import { Loading } from "@/components/shared/loading";
import { getApiClient } from "@/lib/utils";
import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { toast } from "sonner";

export function Activation() {
    const [searchParams] = useSearchParams()
    const userId = searchParams.get('user_id');
    const token = searchParams.get('token');
    const tenantId = searchParams.get('tenant_id');
    const navigate = useNavigate();
    useEffect(() => {
        console.log("Activating account for user:", userId, "with token:", token, "and tenantId:", tenantId);
        async function activate() {
            if (!userId && !token) {
                navigate('/login');
                toast.error("Invalid activation link", { duration: 5000, position: "top-right", richColors: true });
                return;
            }
            const apiClient = getApiClient();
            try {
                await apiClient.account.activateAccountApiV1AccountActivatePost({
                    requestBody: {
                        token: token!
                    },
                    tenantId

                });

                toast.success("Account activated successfully. Please login.", { duration: 5000, position: "top-right", richColors: true });
            } catch (error) {

                toast.error("Account activation failed. Please try again.", { duration: 5000, position: "top-right", richColors: true });
            }
            finally {
                navigate('/login');
            }
        }

        activate();

    }, [userId, token, tenantId]);
    return <Loading variant="dots" />;
}