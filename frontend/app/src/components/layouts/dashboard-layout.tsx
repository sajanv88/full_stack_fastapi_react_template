import {
    SidebarTrigger, SidebarProvider,
} from "@/components/ui/sidebar";
import { Outlet } from 'react-router';

import { DarkMode } from "@/components/features/dark-mode/dark-mode";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { useAuthContext } from "@/components/providers/auth-provider";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { InfoIcon } from "lucide-react"
import { Toaster } from "sonner";
import { SimpleFooter } from "@/components/shared/simple-footer";
import { DashboardSidebar } from "@/components/layouts/dashboard-sidebar-layout";




export function DashboardLayout() {
    const auth = useAuthContext();
    const userImage = auth.user?.image_url ? auth.user?.image_url : "https://github.com/evilrabbit.png";
    return (
        <div className="">
            <SidebarProvider>
                <DashboardSidebar />
                <main className="flex min-h-screen bg-muted w-full">
                    <SidebarTrigger />
                    <section className="w-full h-full flex flex-col">
                        <div className="flex-1 flex-col p-4">
                            <header className="flex items-center">
                                <Avatar>
                                    <AvatarImage src={userImage} />
                                    <AvatarFallback>{auth.user?.first_name[0]}</AvatarFallback>
                                </Avatar>
                                <span className="ml-2 mr-auto flex-1 capitalize flex flex-col">
                                    Welcome {auth.user?.last_name} | Your role: {auth.user?.role?.name}
                                    <em className="text-xs text-muted-foreground">
                                        {auth.user?.role?.name === "guest" && "You are currently a guest user. So, you can only view read-only content."}
                                        {auth.user?.role?.name === "user" && "You are currently a regular user. So, you can view and edit your own content. Sometimes, edit others if you have permission."}
                                        {auth.user?.role?.name === "admin" && "You are currently an admin user. So, you have full access to all resources."}
                                    </em>
                                </span>
                                <DarkMode />
                            </header>

                            <section className="pt-10 flex-1">
                                {!auth.user?.is_active && (
                                    <Alert variant="destructive" className="mb-4">
                                        <InfoIcon className="h-4 w-4" />
                                        <AlertTitle>Your account is not activated</AlertTitle>
                                        <AlertDescription>Please check your email for the activation link.</AlertDescription>
                                    </Alert>
                                )}
                                <Outlet />
                                <Toaster />

                            </section>

                        </div>
                        <SimpleFooter />

                    </section>

                </main>

            </SidebarProvider>

        </div>
    )
}