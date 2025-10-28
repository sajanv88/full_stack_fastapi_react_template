import { useEffect, useState } from "react";
import { useAuthContext } from "@/components/providers/auth-provider";
import { getApiClient } from "@/lib/utils";
import { ProductDto, CreateProductDto } from "@/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Alert, AlertDescription } from "@/components/ui/alert";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import {
    Package,
    Plus,
    RefreshCw,
    Edit,
    Trash2,
    CheckCircle2,
    XCircle,
    Tag,
} from "lucide-react";
import { ShowScreenLoader } from "@/components/shared/show-screen-loader";
import { useStripeProvider } from "@/components/providers/stripe-provider";
import { useAppConfig } from "@/components/providers/app-config-provider";
import { ConfigureStripeNow } from "./configure-stripe-now";

const productSchema = z.object({
    name: z.string().min(1, "Product name is required"),
    description: z.string().min(1, "Description is required"),
    tax_code: z.string().optional(),
    active: z.boolean(),
});

type ProductForm = z.infer<typeof productSchema>;

export function Products() {
    const { accessToken } = useAuthContext();
    const [products, setProducts] = useState<ProductDto[]>([]);
    const [loading, setLoading] = useState(true);
    const [showActiveOnly, setShowActiveOnly] = useState(true);
    const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
    const [editingProduct, setEditingProduct] = useState<ProductDto | null>(null);
    const [deletingProduct, setDeleteProductDialog] = useState<ProductDto | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const [productsError, setProductsError] = useState<string | null>(null);
    const { loading: stripeLoading, stripeConfigurationError, configuredStripeSetting } = useStripeProvider();
    const { current_tenant } = useAppConfig();


    const {
        register,
        handleSubmit,
        setValue,
        watch,
        reset,
        formState: { errors },
    } = useForm<ProductForm>({
        resolver: zodResolver(productSchema),
        defaultValues: {
            name: "",
            description: "",
            tax_code: "",
            active: true,
        },
    });

    const activeValue = watch("active");

    const fetchProducts = async () => {
        if (!accessToken) return;
        setProductsError(null);
        try {
            setLoading(true);
            const response = await getApiClient(accessToken).stripeProducts.listProductsApiV1ProductsGet({
                active: showActiveOnly,
            });
            setProducts(response.products);
        } catch (error) {
            console.error("Error fetching products:", error);
            setProductsError("Failed to fetch products, please try again.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (accessToken && current_tenant && configuredStripeSetting) {
            fetchProducts();
        } else if (!current_tenant) {
            // This is to handle cases where there is no tenant (Host Mode)
            fetchProducts();
        }
    }, [accessToken, showActiveOnly, current_tenant]);

    const openCreateDialog = () => {
        reset({
            name: "",
            description: "",
            tax_code: "",
            active: true,
        });
        setEditingProduct(null);
        setIsCreateDialogOpen(true);
    };

    const openEditDialog = (product: ProductDto) => {
        reset({
            name: product.name,
            description: product.description,
            tax_code: product.tax_code || "",
            active: product.active,
        });
        setEditingProduct(product);
        setIsCreateDialogOpen(true);
    };

    const onSubmit = async (data: ProductForm) => {
        if (!accessToken) return;
        try {
            setSubmitting(true);
            const requestBody: CreateProductDto = {
                name: data.name,
                description: data.description,
                tax_code: data.tax_code || null,
                active: data.active,
            };

            if (editingProduct) {
                await getApiClient(accessToken).stripeProducts.updateProductApiV1ProductsProductIdPatch({
                    productId: editingProduct.id,
                    requestBody,
                });
                toast.success("Product updated successfully", { richColors: true, position: "top-right" });
            } else {
                await getApiClient(accessToken).stripeProducts.createProductApiV1ProductsPost({
                    requestBody,
                });
                toast.success("Product created successfully", { richColors: true, position: "top-right" });
            }

            setIsCreateDialogOpen(false);
            fetchProducts();
        } catch (error) {
            console.error("Error saving product:", error);
            toast.error("Failed to save product", { richColors: true, position: "top-right" });
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async () => {
        if (!accessToken || !deletingProduct) return;
        try {
            setSubmitting(true);
            await getApiClient(accessToken).stripeProducts.deleteProductApiV1ProductsProductIdDelete({
                productId: deletingProduct.id,
            });
            toast.success("Product deleted successfully", { richColors: true, position: "top-right" });
            setDeleteProductDialog(null);
            fetchProducts();
        } catch (error) {
            console.error("Error deleting product:", error);
            toast.error("Failed to delete product", { richColors: true, position: "top-right" });
        } finally {
            setSubmitting(false);
        }
    };

    if ((stripeLoading || loading) && !stripeConfigurationError) {
        return <ShowScreenLoader message="Loading products..." />
    }

    // This check is to prompt user to configure Stripe if there is a configuration error for the tenant
    if (stripeConfigurationError && current_tenant) {
        return <ConfigureStripeNow />
    }


    if (productsError) {
        return (
            <Alert variant="destructive">
                <Package className="h-4 w-4" />
                <AlertDescription>
                    {productsError}
                </AlertDescription>
            </Alert>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                        <Package className="h-6 w-6" />
                        Products
                    </h2>
                    <p className="text-muted-foreground mt-1">
                        Manage your Stripe products and offerings
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button onClick={fetchProducts} variant="outline" size="sm">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                    </Button>
                    <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                        <DialogTrigger asChild>
                            <Button onClick={openCreateDialog}>
                                <Plus className="h-4 w-4 mr-2" />
                                Create Product
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <form onSubmit={handleSubmit(onSubmit)}>
                                <DialogHeader>
                                    <DialogTitle>
                                        {editingProduct ? "Edit Product" : "Create New Product"}
                                    </DialogTitle>
                                    <DialogDescription>
                                        {editingProduct
                                            ? "Update the product details below"
                                            : "Add a new product to your Stripe catalog"}
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="space-y-4 py-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="name">
                                            Product Name <span className="text-destructive">*</span>
                                        </Label>
                                        <Input
                                            id="name"
                                            placeholder="e.g., Premium Subscription"
                                            {...register("name")}
                                        />
                                        {errors.name && (
                                            <p className="text-sm text-destructive">{errors.name.message}</p>
                                        )}
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="description">
                                            Description <span className="text-destructive">*</span>
                                        </Label>
                                        <Textarea
                                            id="description"
                                            placeholder="Describe your product..."
                                            rows={3}
                                            {...register("description")}
                                        />
                                        {errors.description && (
                                            <p className="text-sm text-destructive">{errors.description.message}</p>
                                        )}
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="tax_code">Tax Code (Optional)</Label>
                                        <Input
                                            id="tax_code"
                                            placeholder="e.g., txcd_10000000"
                                            {...register("tax_code")}
                                        />
                                        <p className="text-xs text-muted-foreground">
                                            Stripe tax code for this product
                                        </p>
                                    </div>

                                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                                        <div className="space-y-0.5">
                                            <Label htmlFor="active">Active Status</Label>
                                            <p className="text-sm text-muted-foreground">
                                                Make this product available for purchase
                                            </p>
                                        </div>
                                        <Switch
                                            id="active"
                                            checked={activeValue}
                                            onCheckedChange={(checked) => setValue("active", checked)}
                                        />
                                    </div>
                                </div>
                                <DialogFooter>
                                    <Button
                                        type="button"
                                        variant="outline"
                                        onClick={() => setIsCreateDialogOpen(false)}
                                        disabled={submitting}
                                    >
                                        Cancel
                                    </Button>
                                    <Button type="submit" disabled={submitting}>
                                        {submitting ? (
                                            <>
                                                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                                {editingProduct ? "Updating..." : "Creating..."}
                                            </>
                                        ) : (
                                            <>{editingProduct ? "Update Product" : "Create Product"}</>
                                        )}
                                    </Button>
                                </DialogFooter>
                            </form>
                        </DialogContent>
                    </Dialog>
                </div>
            </div>

            {/* Filter */}
            <Card>
                <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Label htmlFor="show-active">Show Active Only</Label>
                            <Switch
                                id="show-active"
                                checked={showActiveOnly}
                                onCheckedChange={setShowActiveOnly}
                            />
                        </div>
                        <p className="text-sm text-muted-foreground">
                            {products.length} {products.length === 1 ? "product" : "products"}
                        </p>
                    </div>
                </CardContent>
            </Card>

            {/* Products Grid */}
            {products.length === 0 ? (
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-center py-12">
                            <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                            <h3 className="text-lg font-semibold mb-2">No Products Found</h3>
                            <p className="text-muted-foreground text-sm mb-4">
                                {showActiveOnly
                                    ? "No active products available. Try showing all products."
                                    : "Create your first product to get started"}
                            </p>
                            {!showActiveOnly && (
                                <Button onClick={openCreateDialog}>
                                    <Plus className="h-4 w-4 mr-2" />
                                    Create Your First Product
                                </Button>
                            )}
                        </div>
                    </CardContent>
                </Card>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {products.map((product) => (
                        <Card key={product.id} className="relative">
                            <CardHeader className="pb-3">
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2">
                                            <Badge
                                                variant={product.active ? "default" : "secondary"}
                                                className="flex items-center gap-1"
                                            >
                                                {product.active ? (
                                                    <>
                                                        <CheckCircle2 className="h-3 w-3" />
                                                        Active
                                                    </>
                                                ) : (
                                                    <>
                                                        <XCircle className="h-3 w-3" />
                                                        Inactive
                                                    </>
                                                )}
                                            </Badge>
                                        </div>
                                        <CardTitle className="text-lg line-clamp-2">{product.name}</CardTitle>
                                        <CardDescription className="text-sm mt-1 line-clamp-2">
                                            {product.description}
                                        </CardDescription>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-3">
                                {product.tax_code && (
                                    <div className="flex items-center gap-2 p-2 bg-muted rounded-lg">
                                        <Tag className="h-4 w-4 text-muted-foreground" />
                                        <div>
                                            <p className="text-xs text-muted-foreground">Tax Code</p>
                                            <p className="text-sm font-mono">{product.tax_code}</p>
                                        </div>
                                    </div>
                                )}
                                <div className="space-y-1">
                                    <p className="text-xs text-muted-foreground">Product ID</p>
                                    <p className="text-xs font-mono bg-muted p-2 rounded truncate">{product.id}</p>
                                </div>
                                <div className="flex gap-2 pt-2">
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="flex-1"
                                        onClick={() => openEditDialog(product)}
                                    >
                                        <Edit className="h-4 w-4 mr-2" />
                                        Edit
                                    </Button>
                                    <Button
                                        variant="outline"
                                        size="sm"
                                        className="flex-1 text-destructive hover:text-destructive"
                                        onClick={() => setDeleteProductDialog(product)}
                                    >
                                        <Trash2 className="h-4 w-4 mr-2" />
                                        Delete
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            {/* Delete Confirmation Dialog */}
            <AlertDialog open={!!deletingProduct} onOpenChange={() => setDeleteProductDialog(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This will permanently delete the product{" "}
                            <strong className="font-semibold">{deletingProduct?.name}</strong>. This action cannot be
                            undone.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel disabled={submitting}>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={handleDelete}
                            disabled={submitting}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                            {submitting ? (
                                <>
                                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                    Deleting...
                                </>
                            ) : (
                                "Delete Product"
                            )}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}