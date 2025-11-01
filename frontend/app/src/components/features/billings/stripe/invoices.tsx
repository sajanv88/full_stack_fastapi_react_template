import { useEffect, useState } from "react";
import { useAuthContext } from "@/components/providers/auth-provider";
import { formatDate, formatPrice, getApiClient } from "@/lib/utils";
import { InvoiceDto } from "@/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
    Calendar,
    User,
    FileText,
    RefreshCw,
    Download,
    CheckCircle2,
    Clock,
    XCircle,
    AlertCircle,
} from "lucide-react";
import { IconCurrencyEuro, IconReceiptEuro } from "@tabler/icons-react"
import { useStripeProvider } from "@/components/providers/stripe-provider";
import { useAppConfig } from "@/components/providers/app-config-provider";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ShowScreenLoader } from "@/components/shared/show-screen-loader";
import { ConfigureStripeNow } from "./configure-stripe-now";

export function Invoices() {
    const { configuredStripeSetting, loading: stripeLoading, stripeConfigurationError } = useStripeProvider();
    const { current_tenant } = useAppConfig();

    const { accessToken } = useAuthContext();
    const [invoices, setInvoices] = useState<InvoiceDto[]>([]);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(false);
    const [invoiceError, setInvoiceError] = useState<string | null>(null);

    const fetchInvoices = async () => {
        if (!accessToken) return;
        try {
            setLoading(true);
            const response = await getApiClient(accessToken).stripeInvoices.listInvoicesApiV1InvoicesGet();
            setInvoices(response.invoices);
            setHasMore(response.has_more ?? false);
        } catch (error) {
            console.error("Error fetching invoices:", error);
            setInvoiceError("Failed to load invoices. Please try again later.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (accessToken && current_tenant && configuredStripeSetting) {
            fetchInvoices();
        } else if (!current_tenant) {
            // This is to handle cases where there is no tenant (Host Mode)
            fetchInvoices();
        }
    }, [accessToken, current_tenant, configuredStripeSetting]);


    const getStatusBadge = (status: string) => {
        const statusConfig: Record<string, { variant: "default" | "secondary" | "destructive" | "outline", icon: React.ReactNode, label: string }> = {
            paid: {
                variant: "default",
                icon: <CheckCircle2 className="h-3 w-3" />,
                label: "Paid",
            },
            open: {
                variant: "secondary",
                icon: <Clock className="h-3 w-3" />,
                label: "Open",
            },
            draft: {
                variant: "outline",
                icon: <FileText className="h-3 w-3" />,
                label: "Draft",
            },
            void: {
                variant: "destructive",
                icon: <XCircle className="h-3 w-3" />,
                label: "Void",
            },
            uncollectible: {
                variant: "destructive",
                icon: <AlertCircle className="h-3 w-3" />,
                label: "Uncollectible",
            },
        };

        const config = statusConfig[status.toLowerCase()] || {
            variant: "outline" as const,
            icon: <AlertCircle className="h-3 w-3" />,
            label: status,
        };

        return (
            <Badge variant={config.variant} className="flex items-center gap-1 w-fit">
                {config.icon}
                {config.label}
            </Badge>
        );
    };

    if ((stripeLoading || loading) && !stripeConfigurationError) {
        return <ShowScreenLoader message="Loading invoices..." />
    }



    if (invoiceError) {
        return (
            <Alert variant="destructive">
                <IconReceiptEuro className="h-4 w-4" />
                <AlertDescription>
                    {invoiceError}
                </AlertDescription>
            </Alert>
        );
    }

    // This check is to prompt user to configure Stripe if there is a configuration error for the tenant
    if (stripeConfigurationError && current_tenant) {
        return <ConfigureStripeNow />
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                        <IconReceiptEuro className="h-6 w-6" />
                        Invoices
                    </h2>
                    <p className="text-muted-foreground mt-1">
                        View and manage all your billing invoices
                    </p>
                </div>
                <Button onClick={fetchInvoices} variant="outline" className="hidden sm:inline-flex">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                </Button>
                <Button onClick={fetchInvoices} variant="outline" className="sm:hidden" size="icon">
                    <RefreshCw className="h-4 w-4" />
                </Button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Invoices</p>
                                <p className="text-2xl font-bold mt-1">{invoices.length}</p>
                            </div>
                            <IconReceiptEuro className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Paid</p>
                                <p className="text-2xl font-bold mt-1 text-green-600">
                                    {invoices.filter((i) => i.status === "paid").length}
                                </p>
                            </div>
                            <CheckCircle2 className="h-8 w-8 text-green-600" />
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Open</p>
                                <p className="text-2xl font-bold mt-1 text-yellow-600">
                                    {invoices.filter((i) => i.status === "open").length}
                                </p>
                            </div>
                            <Clock className="h-8 w-8 text-yellow-600" />
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Amount</p>
                                <p className="text-2xl font-bold mt-1">
                                    {invoices.length > 0
                                        ? formatPrice(
                                            invoices.reduce((sum, inv) => sum + inv.total, 0),
                                            invoices[0]?.currency || "EUR"
                                        )
                                        : "€0.00"}
                                </p>
                            </div>
                            <IconCurrencyEuro className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Invoices Table */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5" />
                        Invoice History
                    </CardTitle>
                    <CardDescription>
                        {invoices.length} {invoices.length === 1 ? "invoice" : "invoices"}
                        {hasMore && " (showing partial results)"}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {invoices.length === 0 ? (
                        <div className="text-center py-12">
                            <IconReceiptEuro className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                            <h3 className="text-lg font-semibold mb-2">No Invoices Found</h3>
                            <p className="text-muted-foreground text-sm">
                                You don't have any invoices yet
                            </p>
                        </div>
                    ) : (
                        <div className="rounded-md border">
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>Invoice ID</TableHead>
                                        <TableHead>Customer</TableHead>
                                        <TableHead>Date</TableHead>
                                        <TableHead>Amount</TableHead>
                                        <TableHead>Status</TableHead>
                                        <TableHead>Details</TableHead>
                                        <TableHead className="text-right">Actions</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {invoices.map((invoice) => (
                                        <TableRow key={invoice.id}>
                                            <TableCell className="font-mono text-sm">
                                                {invoice.receipt_number || invoice.id.slice(-8)}
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex items-center gap-2">
                                                    <User className="h-4 w-4 text-muted-foreground" />
                                                    <div>
                                                        <p className="font-medium">{invoice.customer_name}</p>
                                                        <p className="text-xs text-muted-foreground">
                                                            {invoice.account_name}
                                                        </p>
                                                    </div>
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex items-center gap-2">
                                                    <Calendar className="h-4 w-4 text-muted-foreground" />
                                                    {formatDate(invoice.created)}
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <div className="font-semibold">
                                                    {formatPrice(invoice.total, invoice.currency)}
                                                </div>
                                                {invoice.amount_paid != null && invoice.amount_paid > 0 && (
                                                    <p className="text-xs text-muted-foreground">
                                                        Paid: {formatPrice(invoice.amount_paid, invoice.currency)}
                                                    </p>
                                                )}
                                            </TableCell>
                                            <TableCell>{getStatusBadge(invoice.status)}</TableCell>
                                            <TableCell>
                                                <div className="space-y-1 text-xs">
                                                    <div className="flex items-center gap-1">
                                                        <span className="text-muted-foreground">Reason:</span>
                                                        <span className="capitalize">
                                                            {invoice.billing_reason.replace("_", " ")}
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center gap-1">
                                                        <span className="text-muted-foreground">Method:</span>
                                                        <span className="capitalize">
                                                            {invoice.collection_method}
                                                        </span>
                                                    </div>
                                                    {invoice.attempt_count != null && invoice.attempt_count > 0 && (
                                                        <div className="flex items-center gap-1">
                                                            <span className="text-muted-foreground">Attempts:</span>
                                                            <span>{invoice.attempt_count}</span>
                                                        </div>
                                                    )}
                                                </div>
                                            </TableCell>
                                            <TableCell className="text-right">
                                                <Button variant="ghost" size="sm">
                                                    <Download className="h-4 w-4 mr-2" />
                                                    Download
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}