import { useEffect, useState } from "react";
import { useAuthContext } from "@/components/providers/auth-provider";
import { formatDateWithHourAndMinute, formatPrice, getApiClient } from "@/lib/utils";
import { BillingRecordDto } from "@/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
    ShoppingCart,
    RefreshCw,
    CheckCircle2,
    Clock,
    XCircle,
    AlertTriangle,
    User,
    Calendar,
    CreditCard,
    TrendingUp,
    Package,
    ArrowLeft,
    ArrowRight,
} from "lucide-react";
import { ShowScreenLoader } from "@/components/shared/show-screen-loader";
import { useLocation, useNavigate } from "react-router";

export function CheckoutOverview() {
    const { accessToken } = useAuthContext();
    const [records, setRecords] = useState<BillingRecordDto[]>([]);
    const [loading, setLoading] = useState(true);
    const { search, pathname } = useLocation();
    const navigate = useNavigate();

    const searchQuery = new URLSearchParams(search);
    const initialSkip = parseInt(searchQuery.get("skip") || "0", 10);
    const initialLimit = parseInt(searchQuery.get("limit") || "10", 10);

    const [pagination, setPagination] = useState({
        skip: initialSkip,
        limit: initialLimit,
        total: 0,
        hasPrevious: false,
        hasNext: false,
    });

    const fetchCheckoutRecords = async (skip: number = 0) => {
        if (!accessToken) return;
        try {
            setLoading(true);
            const response = await getApiClient(accessToken).stripeCheckout.listCheckoutRecordsApiV1CheckoutsAllGet({
                skip,
                limit: pagination.limit,
            });
            setRecords(response.billing_records);
            setPagination({
                skip: response.skip,
                limit: response.limit,
                total: response.total,
                hasPrevious: response.hasPrevious,
                hasNext: response.hasNext,
            });
        } catch (error) {
            console.error("Error fetching checkout records:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (accessToken) {
            fetchCheckoutRecords();
        }
    }, [accessToken, search]);

    const handlePrevious = () => {
        const newSkip = Math.max(0, pagination.skip - pagination.limit);
        const query = new URLSearchParams(window.location.search);
        query.set("skip", newSkip.toString());
        query.set("limit", pagination.limit.toString());
        const newUrl = `${pathname}?${query.toString()}`;
        navigate(newUrl);
    };

    const handleNext = () => {
        const newSkip = pagination.skip + pagination.limit;
        const query = new URLSearchParams(window.location.search);
        query.set("skip", newSkip.toString());
        query.set("limit", pagination.limit.toString());
        const newUrl = `${pathname}?${query.toString()}`;
        navigate(newUrl);
    };



    const getStatusBadge = (status: string) => {
        const statusConfig: Record<
            string,
            { variant: "default" | "secondary" | "destructive" | "outline"; icon: React.ReactNode; label: string }
        > = {
            succeeded: {
                variant: "default",
                icon: <CheckCircle2 className="h-3 w-3" />,
                label: "Succeeded",
            },
            active: {
                variant: "default",
                icon: <CheckCircle2 className="h-3 w-3" />,
                label: "Active",
            },
            pending: {
                variant: "secondary",
                icon: <Clock className="h-3 w-3" />,
                label: "Pending",
            },
            incomplete: {
                variant: "secondary",
                icon: <Clock className="h-3 w-3" />,
                label: "Incomplete",
            },
            requires_payment_method: {
                variant: "outline",
                icon: <CreditCard className="h-3 w-3" />,
                label: "Requires Payment",
            },
            requires_action: {
                variant: "outline",
                icon: <AlertTriangle className="h-3 w-3" />,
                label: "Requires Action",
            },
            payment_failed: {
                variant: "destructive",
                icon: <XCircle className="h-3 w-3" />,
                label: "Payment Failed",
            },
            canceled: {
                variant: "destructive",
                icon: <XCircle className="h-3 w-3" />,
                label: "Canceled",
            },
        };

        const config = statusConfig[status.toLowerCase()] || {
            variant: "outline" as const,
            icon: <AlertTriangle className="h-3 w-3" />,
            label: status,
        };

        return (
            <Badge variant={config.variant} className="flex items-center gap-1 w-fit">
                {config.icon}
                {config.label}
            </Badge>
        );
    };

    const getScopeBadge = (scope: string) => {
        return (
            <Badge variant="outline" className="capitalize">
                {scope}
            </Badge>
        );
    };

    const getPaymentTypeBadge = (type: string) => {
        return (
            <Badge variant="secondary" className="capitalize">
                {type.replace("_", " ")}
            </Badge>
        );
    };

    if (loading) {
        return <ShowScreenLoader message="Loading checkouts list..." />
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                        <ShoppingCart className="h-6 w-6" />
                        Checkout Overview
                    </h2>
                    <p className="text-muted-foreground mt-1">
                        View and manage all checkout sessions and billing records
                    </p>
                </div>
                <Button onClick={() => fetchCheckoutRecords(pagination.skip)} variant="outline" className="hidden sm:inline-flex">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                </Button>
                <Button onClick={() => fetchCheckoutRecords(pagination.skip)} variant="outline" className="sm:hidden">
                    <RefreshCw className="h-4 w-4" />
                </Button>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Records</p>
                                <p className="text-2xl font-bold mt-1">{pagination.total}</p>
                            </div>
                            <ShoppingCart className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Succeeded</p>
                                <p className="text-2xl font-bold mt-1 text-green-600">
                                    {records.filter((r) => r.status === "succeeded" || r.status === "active").length}
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
                                <p className="text-sm text-muted-foreground">Pending</p>
                                <p className="text-2xl font-bold mt-1 text-yellow-600">
                                    {records.filter((r) => r.status === "pending" || r.status === "incomplete").length}
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
                                <p className="text-sm text-muted-foreground">Failed/Canceled</p>
                                <p className="text-2xl font-bold mt-1 text-red-600">
                                    {
                                        records.filter((r) => r.status === "payment_failed" || r.status === "canceled")
                                            .length
                                    }
                                </p>
                            </div>
                            <XCircle className="h-8 w-8 text-red-600" />
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Records Table */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle className="flex items-center gap-2">
                                <TrendingUp className="h-5 w-5" />
                                Checkout Records
                            </CardTitle>
                            <CardDescription>
                                Showing {pagination.skip + 1} to {Math.min(pagination.skip + pagination.limit, pagination.total)} of{" "}
                                {pagination.total} records
                            </CardDescription>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {records.length === 0 ? (
                        <div className="text-center py-12">
                            <ShoppingCart className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                            <h3 className="text-lg font-semibold mb-2">No Checkout Records Found</h3>
                            <p className="text-muted-foreground text-sm">There are no checkout sessions yet</p>
                        </div>
                    ) : (
                        <>
                            <div className="rounded-md border">
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Scope</TableHead>
                                            <TableHead>Actor</TableHead>
                                            <TableHead>Payment Type</TableHead>
                                            <TableHead>Amount</TableHead>
                                            <TableHead>Status</TableHead>
                                            <TableHead>Customer</TableHead>
                                            <TableHead>Details</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {records.map((record, index) => (
                                            <TableRow key={index}>
                                                <TableCell>{getScopeBadge(record.scope)}</TableCell>
                                                <TableCell>
                                                    <div className="flex items-center gap-2">
                                                        <User className="h-4 w-4 text-muted-foreground" />
                                                        <span className="capitalize">{record.actor.replace("_", " ")}</span>
                                                    </div>
                                                </TableCell>
                                                <TableCell>{getPaymentTypeBadge(record.payment_type)}</TableCell>
                                                <TableCell>
                                                    <div className="font-semibold">
                                                        {formatPrice(record.amount || 0, record.currency)}
                                                    </div>
                                                </TableCell>
                                                <TableCell>{getStatusBadge(record.status)}</TableCell>
                                                <TableCell>
                                                    {record.stripe_customer_id ? (
                                                        <div className="space-y-1">
                                                            <p className="text-xs font-mono">
                                                                {record.stripe_customer_id.slice(0, 20)}...
                                                            </p>
                                                            {record.user_id && (
                                                                <p className="text-xs text-muted-foreground">
                                                                    User: {record.user_id.slice(0, 8)}...
                                                                </p>
                                                            )}
                                                        </div>
                                                    ) : (
                                                        <span className="text-muted-foreground">N/A</span>
                                                    )}
                                                </TableCell>
                                                <TableCell>
                                                    <div className="space-y-1 text-xs">
                                                        {record.stripe_subscription_id && (
                                                            <div className="flex items-center gap-1">
                                                                <CreditCard className="h-3 w-3 text-muted-foreground" />
                                                                <span className="text-muted-foreground">Sub:</span>
                                                                <span className="font-mono">
                                                                    {record.stripe_subscription_id.slice(0, 10)}...
                                                                </span>
                                                            </div>
                                                        )}
                                                        {record.product_id && (
                                                            <div className="flex items-center gap-1">
                                                                <Package className="h-3 w-3 text-muted-foreground" />
                                                                <span className="text-muted-foreground">Product:</span>
                                                                <span className="font-mono">
                                                                    {record.product_id.slice(0, 10)}...
                                                                </span>
                                                            </div>
                                                        )}
                                                        {record.current_period_end && (
                                                            <div className="flex items-center gap-1">
                                                                <Calendar className="h-3 w-3 text-muted-foreground" />
                                                                <span className="text-muted-foreground">Ends:</span>
                                                                <span>{formatDateWithHourAndMinute(record.current_period_end)}</span>
                                                            </div>
                                                        )}
                                                        {record.canceled_at && (
                                                            <div className="flex items-center gap-1">
                                                                <XCircle className="h-3 w-3 text-destructive" />
                                                                <span className="text-destructive">Canceled:</span>
                                                                <span>{formatDateWithHourAndMinute(record.canceled_at)}</span>
                                                            </div>
                                                        )}
                                                        {record.cancellation_reason && (
                                                            <p className="text-muted-foreground italic">
                                                                Reason: {record.cancellation_reason}
                                                            </p>
                                                        )}
                                                    </div>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>

                            {/* Pagination */}
                            {pagination.total > pagination.limit && (
                                <div className="flex items-center justify-between mt-4">
                                    <p className="text-sm text-muted-foreground">
                                        Page {Math.floor(pagination.skip / pagination.limit) + 1} of{" "}
                                        {Math.ceil(pagination.total / pagination.limit)}
                                    </p>
                                    <div className="flex items-center gap-2">
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={handlePrevious}
                                            disabled={!pagination.hasPrevious}
                                        >
                                            <ArrowLeft className="h-4 w-4 mr-2" />
                                            Previous
                                        </Button>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={handleNext}
                                            disabled={!pagination.hasNext}
                                        >
                                            Next
                                            <ArrowRight className="h-4 w-4 ml-2" />
                                        </Button>
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}