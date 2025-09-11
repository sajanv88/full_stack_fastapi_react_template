
import { NavLink, useLocation, useNavigate } from 'react-router';
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
import { Button } from "../ui/button";
import { clearAllTokens } from "@/lib/utils";
import { Logo } from "@/components/shared/logo";
import {
    LayoutDashboard,
    Users,
    Shield,
    User,
    MessageSquare,
    LogOut,
    ChevronRight,
    Tent,
    Cog
} from 'lucide-react';
import { useAuthContext } from '../providers/auth-provider';
import { useMemo } from 'react';

const navLinks = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/users?skip=0&limit=10", label: "Users", icon: Users },
    { href: "/roles?skip=0&limit=10", label: "Roles", icon: Shield },
    { href: "/tenants?skip=0&limit=10", label: "Tenants", icon: Tent },
    { href: "/settings", label: "Settings", icon: Cog },
];

const bottomLinks = [
    { href: "/profile", label: "Profile", icon: User },
    { href: "/ai", label: "AI Chat", icon: MessageSquare },
];


export function DashboardSidebar() {
    const location = useLocation();
    const pathname = location.pathname;
    const navigate = useNavigate();
    const { user } = useAuthContext();
    const isTenant = user?.tenant_id;

    function isLinkActive(href: string) {
        if (href.includes('?')) {
            const basePath = href.split('?')[0];
            return pathname === basePath;
        }
        return pathname === href;
    };

    function logout() {
        clearAllTokens();
        navigate("/login");
    };

    const mainNavLinksToRender = useMemo(() => isTenant ? navLinks.filter(link => !link.href.includes('/tenants')) : navLinks, [isTenant]);

    return (
        <Sidebar>
            <SidebarHeader className="pb-6 pt-6 px-4">
                <NavLink
                    to="/dashboard"
                    className="text-2xl font-bold tracking-tight text-primary hover:text-primary/80 transition-colors flex items-center justify-center"
                >
                    <Logo />
                </NavLink>
            </SidebarHeader>
            <SidebarContent>
                <SidebarMenu>
                    {mainNavLinksToRender.map((link) => (
                        <SidebarMenuItem key={link.href}>
                            <SidebarMenuButton
                                asChild
                                isActive={isLinkActive(link.href)}
                                className="group relative"
                            >
                                <NavLink to={link.href} className="w-full flex items-center space-x-3">
                                    <link.icon className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                                    <span className="group-hover:translate-x-0.5 transition-transform">{link.label}</span>
                                    {isLinkActive(link.href) && (
                                        <ChevronRight className="w-4 h-4 ml-auto text-primary" />
                                    )}
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
                                isActive={isLinkActive(link.href)}
                                className="group relative"
                            >
                                <NavLink to={link.href} className="w-full flex items-center space-x-3">
                                    <link.icon className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                                    <span className="group-hover:translate-x-0.5 transition-transform">{link.label}</span>
                                    {isLinkActive(link.href) && (
                                        <ChevronRight className="w-4 h-4 ml-auto text-primary" />
                                    )}
                                </NavLink>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    ))}

                    <SidebarMenuItem>
                        <SidebarMenuButton
                            asChild
                        >
                            <Button
                                variant="ghost"
                                className="w-full justify-start hover:bg-destructive/10 hover:text-destructive transition-colors group"
                                onClick={logout}
                            >
                                <LogOut className="w-4 h-4 mr-3 text-muted-foreground group-hover:text-destructive transition-colors" />
                                <span className="group-hover:translate-x-0.5 transition-transform">Logout</span>
                            </Button>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarFooter>
        </Sidebar>
    )
}