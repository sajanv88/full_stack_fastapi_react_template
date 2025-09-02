import {
    SidebarTrigger, SidebarProvider,
} from "@/components/ui/sidebar";
import { NavLink, Outlet, useLocation } from 'react-router';
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

const navLinks = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/users", label: "Users" },
    { href: "/roles", label: "Roles" },
];

const bottomLinks = [
    { href: "/profile", label: "Profile" },
    { href: "/dashboard/logout", label: "Logout" },
];


function DashboardSidebar() {
    const location = useLocation();
    const pathname = location.pathname;

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
                </SidebarMenu>
            </SidebarFooter>
        </Sidebar>
    )
}



export function DashboardLayout() {
    return (
        <div className="">
            <SidebarProvider>
                <DashboardSidebar />
                <main className="flex min-h-screen bg-muted w-full">
                    <SidebarTrigger />
                    <div className="flex-1 p-4">
                        <header className="flex justify-end items-center">
                            <DarkMode />
                        </header>
                        <Outlet />
                    </div>
                </main>
            </SidebarProvider>
        </div>
    )
}