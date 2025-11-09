
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
import { IconSettingsBolt, IconCurrencyEuro, IconNotification, IconLogs } from "@tabler/icons-react"
import { useAuthContext } from '../providers/auth-provider';
import { useMemo } from 'react';
import { cn, getApiClient } from '@/lib/utils';
import { toast } from 'sonner';

const navLinks = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/users?skip=0&limit=10", label: "Users", icon: Users },
    { href: "/roles?skip=0&limit=10", label: "Roles", icon: Shield },
    { href: "/tenants?skip=0&limit=10", label: "Tenants", icon: Tent },
    { href: "/audit-logs?skip=0&limit=10", label: "Audit Logs", icon: IconLogs },
    {
        href: "/settings",
        label: "Settings",
        icon: Cog,
        children: [
            { href: "/settings/general", label: "General", icon: IconSettingsBolt, visibility: "tenants" },
            { href: "/settings/payment", label: "Payment", icon: IconCurrencyEuro, visibility: "tenants" },
            { href: "/settings/notifications", label: "Notifications", icon: IconNotification, visibility: "both" },
        ]
    },
];

const bottomLinks = [
    { href: "/profile", label: "Profile", icon: User },
    { href: "/ai", label: "AI Chat", icon: MessageSquare },
    { href: "/billing", label: "Billing", icon: IconCurrencyEuro },
];

type LinkType = typeof navLinks[number];


export function DashboardSidebar() {
    const location = useLocation();
    const pathname = location.pathname;
    const navigate = useNavigate();
    const { user, accessToken } = useAuthContext();
    const isTenant = user?.tenant_id;

    function isLinkActive(href: string) {
        if (href.includes('?')) {
            const basePath = href.split('?')[0];
            return pathname === basePath;
        }
        return pathname.includes(href);
    };

    async function logout() {
        try {
            await getApiClient(accessToken).account.logoutApiV1AccountLogoutGet();
            toast.success("Logged out successfully.",
                { richColors: true, position: "top-right", description: "Redirecting to login..." });
        } catch (error) {
            console.error("Logout failed:", error);
            toast.error("Logout failed. Please try again.", { richColors: true, position: "top-right" });
        } finally {
            setTimeout(() => {
                navigate("/login");
            }, 2000); // Small delay to ensure toast is shown before navigation

        }
    };

    const mainNavLinksToRender = useMemo(() => isTenant ? navLinks.filter(link => !link.href.includes('/tenants')) : navLinks, [isTenant]);
    function renderMainNavLinks(link: LinkType) {

        return (
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
                {(link.children && link.children.length > 0 && isTenant) && (
                    <SidebarMenu className='pl-8 mt-1'>
                        {link.children.map((child) => (
                            <SidebarMenuItem key={child.href}>
                                <SidebarMenuButton
                                    asChild
                                    isActive={isLinkActive(child.href)}
                                    className={cn("group relative")}
                                >
                                    <NavLink to={child.href} className="w-full flex items-center space-x-3">
                                        <child.icon className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                                        <span className="group-hover:translate-x-0.5 transition-transform">{child.label}</span>
                                        {isLinkActive(child.href) && (
                                            <ChevronRight className="w-4 h-4 ml-auto text-primary" />
                                        )}
                                    </NavLink>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                        ))}
                    </SidebarMenu>
                )}

                {(link.children && link.children.length > 0 && !isTenant) && (
                    <SidebarMenu className='pl-8 mt-1'>
                        {link.children.map((child) => (
                            (child.visibility === "both") && (
                                <SidebarMenuItem key={child.href}>
                                    <SidebarMenuButton
                                        asChild
                                        isActive={isLinkActive(child.href)}
                                        className={cn("group relative")}
                                    >
                                        <NavLink to={child.href} className="w-full flex items-center space-x-3">
                                            <child.icon className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                                            <span className="group-hover:translate-x-0.5 transition-transform">{child.label}</span>
                                            {isLinkActive(child.href) && (
                                                <ChevronRight className="w-4 h-4 ml-auto text-primary" />
                                            )}
                                        </NavLink>
                                    </SidebarMenuButton>
                                </SidebarMenuItem>
                            )
                        ))}
                    </SidebarMenu>
                )}
            </SidebarMenuItem>
        )
    }
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
                    {mainNavLinksToRender.map(renderMainNavLinks)}
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