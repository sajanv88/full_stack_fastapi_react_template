import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Plus, RefreshCw, BadgeEuro, Calendar, Package } from "lucide-react";
import { useAuthContext } from "@/components/providers/auth-provider";
import { getApiClient } from "@/lib/utils";
import { ProductDto, CreatePlanDto } from "@/api";

const planSchema = z.object({
    product_id: z.string().min(1, "Product is required"),
    amount: z.number().min(1, "Amount must be greater than 0"),
    currency: z.string().min(3, "Currency must be 3 characters").max(3, "Currency must be 3 characters"),
    interval: z.enum(["month", "year"]),
});

type PlanForm = z.infer<typeof planSchema>;

interface AddANewPlanProps {
    onPlanCreated?: () => void;
}

export function AddANewPlan({ onPlanCreated }: AddANewPlanProps) {
    const { accessToken } = useAuthContext();
    const [isOpen, setIsOpen] = useState(false);
    const [products, setProducts] = useState<ProductDto[]>([]);
    const [loadingProducts, setLoadingProducts] = useState(false);
    const [submitting, setSubmitting] = useState(false);

    const {
        register,
        handleSubmit,
        setValue,
        watch,
        reset,
        formState: { errors },
    } = useForm<PlanForm>({
        resolver: zodResolver(planSchema),
        defaultValues: {
            product_id: "",
            amount: 0,
            currency: "EUR",
            interval: "month",
        },
    });

    const selectedInterval = watch("interval");
    const selectedProductId = watch("product_id");
    const amount = watch("amount");

    const fetchProducts = async () => {
        if (!accessToken) return;
        try {
            setLoadingProducts(true);
            const response = await getApiClient(accessToken).stripeProducts.listProductsApiV1ProductsGet({
                active: true,
            });
            setProducts(response.products);
        } catch (error) {
            console.error("Error fetching products:", error);
            toast.error("Failed to fetch products", { richColors: true, position: "top-right" });
        } finally {
            setLoadingProducts(false);
        }
    };

    useEffect(() => {
        if (isOpen && accessToken) {
            fetchProducts();
        }
    }, [isOpen, accessToken]);

    const formatPreviewPrice = (amountInCents: number, currency: string) => {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: currency.toUpperCase(),
        }).format(amountInCents / 100);
    };

    const onSubmit = async (data: PlanForm) => {
        if (!accessToken) return;
        try {
            setSubmitting(true);
            const requestBody: CreatePlanDto = {
                product_id: data.product_id,
                amount: data.amount,
                currency: data.currency,
                interval: data.interval,
            };

            await getApiClient(accessToken).stripeBilling.createPlanApiV1BillingPlansPost({
                requestBody,
            });

            toast.success("Plan created successfully", { richColors: true, position: "top-right" });
            setIsOpen(false);
            reset();
            onPlanCreated?.();
        } catch (error) {
            console.error("Error creating plan:", error);
            toast.error("Failed to create plan", { richColors: true, position: "top-right" });
        } finally {
            setSubmitting(false);
        }
    };

    const handleOpenChange = (open: boolean) => {
        setIsOpen(open);
        if (!open) {
            reset();
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={handleOpenChange}>
            <DialogTrigger asChild>
                <>
                    <Button className="hidden sm:inline-flex" onClick={() => setIsOpen(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add a Plan
                    </Button>
                    <Button className="sm:hidden" size="icon" onClick={() => setIsOpen(true)}>
                        <Plus className="h-4 w-4" />
                    </Button>
                </>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[550px]">
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2">
                            <Package className="h-5 w-5" />
                            Create New Plan
                        </DialogTitle>
                        <DialogDescription>
                            Create a new pricing plan for your product. Enter the amount in cents (e.g., 2999 for
                            €29.99).
                        </DialogDescription>
                    </DialogHeader>

                    <div className="space-y-4 py-4">
                        {/* Product Selection */}
                        <div className="space-y-2">
                            <Label htmlFor="product_id">
                                Product <span className="text-destructive">*</span>
                            </Label>
                            {loadingProducts ? (
                                <div className="flex items-center gap-2 p-3 border rounded-lg">
                                    <RefreshCw className="h-4 w-4 animate-spin text-muted-foreground" />
                                    <span className="text-sm text-muted-foreground">Loading products...</span>
                                </div>
                            ) : products.length === 0 ? (
                                <div className="p-3 border rounded-lg text-sm text-muted-foreground">
                                    No active products found. Please create a product first.
                                </div>
                            ) : (
                                <Select
                                    value={selectedProductId}
                                    onValueChange={(value) => setValue("product_id", value)}
                                >
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select a product" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {products.map((product) => (
                                            <SelectItem key={product.id} value={product.id}>
                                                <div className="flex items-center gap-2">
                                                    <Package className="h-4 w-4" />
                                                    <span>{product.name}</span>
                                                </div>
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            )}
                            {errors.product_id && (
                                <p className="text-sm text-destructive">{errors.product_id.message}</p>
                            )}
                            <p className="text-xs text-muted-foreground">
                                Select the product this plan will be associated with
                            </p>
                        </div>

                        {/* Amount and Currency */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="amount">
                                    Amount (in cents) <span className="text-destructive">*</span>
                                </Label>
                                <div className="relative">
                                    <BadgeEuro className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                    <Input
                                        id="amount"
                                        type="number"
                                        placeholder="2999"
                                        className="pl-9"
                                        {...register("amount", { valueAsNumber: true })}
                                    />
                                </div>
                                {errors.amount && (
                                    <p className="text-sm text-destructive">{errors.amount.message}</p>
                                )}
                                <p className="text-xs text-muted-foreground">Enter amount in cents (e.g., 2999)</p>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="currency">
                                    Currency <span className="text-destructive">*</span>
                                </Label>
                                <Input
                                    id="currency"
                                    placeholder="EUR"
                                    maxLength={3}
                                    className="uppercase"
                                    {...register("currency")}
                                />
                                {errors.currency && (
                                    <p className="text-sm text-destructive">{errors.currency.message}</p>
                                )}
                                <p className="text-xs text-muted-foreground">3-letter ISO code</p>
                            </div>
                        </div>

                        {/* Billing Interval */}
                        <div className="space-y-2">
                            <Label htmlFor="interval">
                                Billing Interval <span className="text-destructive">*</span>
                            </Label>
                            <Select value={selectedInterval} onValueChange={(value) => setValue("interval", value as "month" | "year")}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select billing interval" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="month">
                                        <div className="flex items-center gap-2">
                                            <Calendar className="h-4 w-4" />
                                            <span>Monthly</span>
                                        </div>
                                    </SelectItem>
                                    <SelectItem value="year">
                                        <div className="flex items-center gap-2">
                                            <Calendar className="h-4 w-4" />
                                            <span>Yearly</span>
                                        </div>
                                    </SelectItem>
                                </SelectContent>
                            </Select>
                            {errors.interval && (
                                <p className="text-sm text-destructive">{errors.interval.message}</p>
                            )}
                            <p className="text-xs text-muted-foreground">How often the customer will be charged</p>
                        </div>

                        {/* Price Preview */}
                        {amount > 0 && (
                            <div className="p-4 bg-muted rounded-lg">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm font-medium">Price Preview</p>
                                        <p className="text-xs text-muted-foreground mt-1">
                                            What customers will see
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-2xl font-bold">
                                            {formatPreviewPrice(amount, watch("currency") || "USD")}
                                        </p>
                                        <p className="text-sm text-muted-foreground">
                                            per {selectedInterval === "month" ? "month" : "year"}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Info Box */}
                        <div className="p-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
                            <p className="text-sm text-blue-900 dark:text-blue-100">
                                <strong>Note:</strong> Once created, the plan will be available for subscription. Make
                                sure all details are correct before creating.
                            </p>
                        </div>
                    </div>

                    <DialogFooter>
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => setIsOpen(false)}
                            disabled={submitting}
                        >
                            Cancel
                        </Button>
                        <Button type="submit" disabled={submitting || products.length === 0}>
                            {submitting ? (
                                <>
                                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                    Creating...
                                </>
                            ) : (
                                <>

                                    Submit
                                </>
                            )}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}