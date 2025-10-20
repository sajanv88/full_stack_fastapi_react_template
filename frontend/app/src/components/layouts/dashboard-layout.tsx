import {
    SidebarTrigger, SidebarProvider,
} from "@/components/ui/sidebar";
import { Outlet, useNavigate } from 'react-router';

import { DarkMode } from "@/components/features/dark-mode/dark-mode";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { useAuthContext } from "@/components/providers/auth-provider";
import { Toaster } from "sonner";
import { SimpleFooter } from "@/components/shared/simple-footer";
import { DashboardSidebar } from "@/components/layouts/dashboard-sidebar-layout";
import { useAppConfig } from "../providers/app-config-provider";
import { Badge } from "@/components/ui/badge";
import { useEffect, useMemo } from "react";
import { Loading } from "../shared/loading";
import { Button } from "../ui/button";




export function DashboardLayout() {
    const navigate = useNavigate();
    const auth = useAuthContext();
    const { current_tenant } = useAppConfig();

    useEffect(() => {
        if (!auth.user) {
            async function init() {
                await auth.refreshCurrentUser();
            }
            init();
        }
    }, [auth.user])

    const userImage = auth.user?.image_url ? auth.user?.image_url : "https://github.com/evilrabbit.png";
    const isHost = useMemo(() => auth.can("host:manage_tenants"), [auth]);

    useEffect(() => {
        if (!auth.isLoggedIn) {
            return;
        }
        if (!current_tenant?.is_active && !isHost) {
            // Redirect to NonActiveTenantView
            navigate("/non-active");
        }
    }, [current_tenant, auth])

    if (!auth.isLoggedIn) {
        return (
            <main className="h-screen flex items-center justify-center">
                <Loading variant="pulse" size="md" />
            </main>
        )
    }
    return (
        <div>
            {!auth.user?.is_active && (
                <div className="px-4 fixed z-50 w-full right-0 bg-secondary flex items-center justify-center">
                    <p className="text-sm  p-0 pr-1 flex justify-center">
                        Your account is not activated.
                        Please check your email for the activation link. Or
                    </p>
                    <Button
                        variant="link" size="sm" className="p-0 text-orange-300"
                        onClick={auth.resendActivationEmail}
                    >
                        Resend Activation Email
                    </Button>
                </div>
            )}
            <SidebarProvider>
                <DashboardSidebar />
                <main className="sm:w-full">
                    <SidebarTrigger />
                    <section className="w-full h-full flex flex-col">

                        <div className="flex-1 flex-col">
                            <header className="flex items-center p-2">
                                <Avatar>
                                    <AvatarImage src={userImage} />
                                    <AvatarFallback>{auth.user?.first_name[0]}</AvatarFallback>
                                </Avatar>
                                <span className="ml-2 mr-auto flex-1 capitalize flex flex-col">
                                    <span className="flex items-center w-[12rem] sm:w-[25rem]">
                                        <span className="flex-1">
                                            Welcome {auth.user?.last_name}
                                        </span>

                                        <span className="flex gap-2">
                                            <Badge variant="secondary">Role: {auth.user?.role?.name}</Badge>
                                            {isHost && (<Badge variant="secondary">Host Access</Badge>)}
                                            {current_tenant && (<Badge variant="secondary">Tenant: {current_tenant?.name}</Badge>)}
                                        </span>
                                    </span>
                                    <em className="text-xs text-muted-foreground mt-2">
                                        {auth.user?.role?.name === "guest" && "You are currently a guest user. So, you can only view read-only content."}
                                        {auth.user?.role?.name === "user" && "You are currently a regular user. So, you can view and edit your own content. Sometimes, edit others if you have permission."}
                                        {auth.user?.role?.name === "admin" && "You are currently an admin user. So, you have full access to all resources."}
                                    </em>

                                </span>
                                <DarkMode />
                            </header>

                            <section className="pt-10 flex-1">

                                <div className="p-2">

                                    <Outlet />
                                    <Toaster />
                                </div>

                            </section>

                        </div>
                        <SimpleFooter />
                    </section>

                </main>

            </SidebarProvider>
        </div>


    )
}