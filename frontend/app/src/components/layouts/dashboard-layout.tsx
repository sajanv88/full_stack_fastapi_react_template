import {
    SidebarTrigger, SidebarProvider,
} from "@/components/ui/sidebar";
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router';
import {
    Sidebar,
    SidebarContent,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuItem,
    SidebarMenuButton,
    SidebarFooter,
    SidebarSeparator,
} from "@/components/ui/sidebar";
import { DarkMode } from "../features/dark-mode/dark-mode";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { useAuthContext } from "@/components/providers/auth-provider";
import { Button } from "../ui/button";
import { clearAllTokens } from "@/lib/utils";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { InfoIcon } from "lucide-react"

const navLinks = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/users?skip=0&limit=10", label: "Users" },
    { href: "/roles?skip=0&limit=10", label: "Roles" },
];

const bottomLinks = [
    { href: "/profile", label: "Profile" },
];


function DashboardSidebar() {
    const location = useLocation();
    const pathname = location.pathname;
    const navigate = useNavigate();

    const logout = () => {
        clearAllTokens();
        navigate("/login");
    };

    return (
        <Sidebar>
            <SidebarHeader>
                <NavLink
                    to="/dashboard"
                    className="text-2xl font-bold tracking-tight text-primary"
                >
                    Full-Stack Fast API
                </NavLink>
            </SidebarHeader>
            <SidebarContent>
                <SidebarMenu>
                    {navLinks.map((link) => (
                        <SidebarMenuItem key={link.href}>
                            <SidebarMenuButton
                                asChild
                                isActive={pathname === link.href}
                            >
                                <NavLink to={link.href} className="w-full">
                                    <span>{link.label}</span>
                                </NavLink>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    ))}
                </SidebarMenu>
            </SidebarContent>
            <SidebarSeparator />
            <SidebarFooter>
                <SidebarMenu>
                    {bottomLinks.map((link) => (
                        <SidebarMenuItem key={link.href}>
                            <SidebarMenuButton
                                asChild
                                isActive={pathname === link.href}
                            >
                                <NavLink to={link.href} className="w-full">
                                    <span>{link.label}</span>
                                </NavLink>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    ))}

                    <SidebarMenuItem>
                        <SidebarMenuButton
                            asChild
                        >
                            <Button variant="link" className="inline hover:no-underline cursor-pointer"
                                onClick={logout}>
                                Logout
                            </Button>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarFooter>
        </Sidebar>
    )
}



export function DashboardLayout() {
    const auth = useAuthContext();
    return (
        <div className="">
            <SidebarProvider>
                <DashboardSidebar />
                <main className="flex min-h-screen bg-muted w-full">
                    <SidebarTrigger />
                    <div className="flex-1 p-4">
                        <header className="flex items-center">
                            <Avatar>
                                <AvatarImage src="https://github.com/evilrabbit.png" />
                                <AvatarFallback>{auth.user?.first_name[0]}</AvatarFallback>
                            </Avatar>
                            <span className="ml-2 mr-auto flex-1 capitalize">
                                Welcome {auth.user?.last_name} | Your role: {auth.user?.role?.name}
                            </span>
                            <DarkMode />
                        </header>

                        <section className="pt-10">
                            {!auth.user?.is_active && (
                                <Alert variant="destructive" className="mb-4">
                                    <InfoIcon className="h-4 w-4" />
                                    <AlertTitle>Your account is not activated</AlertTitle>
                                    <AlertDescription>Please check your email for the activation link.</AlertDescription>
                                </Alert>
                            )}
                            <Outlet />
                        </section>
                    </div>
                </main>
            </SidebarProvider>
        </div>
    )
}