import { StripeProvider } from "@/components/providers/stripe-provider";
import { Tabs, TabsTrigger } from "@/components/ui/tabs";
import { TabsContent, TabsList } from "@radix-ui/react-tabs";
import { NavLink, Outlet, useLocation } from "react-router";


export function Billing() {
    const { pathname } = useLocation()
    return (
        <StripeProvider>
            <Tabs defaultValue={pathname} className="w-full xl:container xl:mx-auto xl:max-w-4xl">
                <TabsList className="mb-2 border-b pb-2 flex">
                    <TabsTrigger asChild value="/billing" className="w-full">
                        <NavLink to="/billing">Overview</NavLink>
                    </TabsTrigger>
                    <TabsTrigger asChild value="/billing/invoices" className="w-full">
                        <NavLink to="/billing/invoices">Invoices</NavLink>
                    </TabsTrigger>
                    <TabsTrigger asChild value="/billing/products" className="w-full">
                        <NavLink to="/billing/products">Products</NavLink>
                    </TabsTrigger>
                    <TabsTrigger asChild value="/billing/checkouts" className="w-full">
                        <NavLink to="/billing/checkouts?skip=0&limit=100">Checkouts</NavLink>
                    </TabsTrigger>
                </TabsList>
                <TabsContent value={pathname}>
                    <Outlet />
                </TabsContent>
            </Tabs>
        </StripeProvider>


    )
}