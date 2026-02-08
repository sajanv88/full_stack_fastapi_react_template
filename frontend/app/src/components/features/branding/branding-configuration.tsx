import { useBrandingContext } from "@/components/providers/branding-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    IconSettingsStar,
    IconPalette,
    IconPhone,
    IconMail,
    IconMapPin,
    IconLoader2,
    IconCheck,
    IconIdBadge2,
    IconUpload,
    IconPhoto,
    IconX
} from "@tabler/icons-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from "@/components/ui/form";
import { useState } from "react";
import type { UpdateBrandingDto } from "@/api";
import ColorField from "@/components/features/branding/color-fields";

const contactInfoSchema = z.object({
    support_email: z.string().email('Invalid email').optional().or(z.literal('')),
    phone: z.string().optional(),
    address: z.string().optional(),
});

const themeColorsSchema = z.object({
    background: z.string().optional(),
    foreground: z.string().optional(),
    primary: z.string().optional(),
    primary_foreground: z.string().optional(),
    secondary: z.string().optional(),
    secondary_foreground: z.string().optional(),
    muted: z.string().optional(),
    muted_foreground: z.string().optional(),
    accent: z.string().optional(),
    accent_foreground: z.string().optional(),
    destructive: z.string().optional(),
    destructive_foreground: z.string().optional(),
    border: z.string().optional(),
    input: z.string().optional(),
    ring: z.string().optional(),
    card: z.string().optional(),
    card_foreground: z.string().optional(),
    popover: z.string().optional(),
    popover_foreground: z.string().optional(),
    chart_1: z.string().optional(),
    chart_2: z.string().optional(),
    chart_3: z.string().optional(),
    chart_4: z.string().optional(),
    chart_5: z.string().optional(),
    sidebar: z.string().optional(),
    sidebar_foreground: z.string().optional(),
    sidebar_primary: z.string().optional(),
    sidebar_primary_foreground: z.string().optional(),
    sidebar_accent: z.string().optional(),
    sidebar_accent_foreground: z.string().optional(),
    sidebar_border: z.string().optional(),
    sidebar_ring: z.string().optional(),
});

export const brandingFormSchema = z.object({
    identity: z.object({
        app_name: z.string().optional(),
    }).optional(),
    contact_info: contactInfoSchema.optional(),
    theme_config: z.object({
        radius: z.string().optional(),
        light: themeColorsSchema.optional(),
        dark: themeColorsSchema.optional(),
    }).optional(),
});

export type BrandingFormValues = z.infer<typeof brandingFormSchema>;

export default function BrandingConfiguration() {
    const { branding, onUpdateBranding, onUploadLogo } = useBrandingContext();
    const [loading, setLoading] = useState(false);
    const [saved, setSaved] = useState(false);
    const [logoFile, setLogoFile] = useState<File | null>(null);
    const [logoPreview, setLogoPreview] = useState<string | null>(branding?.logo_url || null);
    const [uploadingLogo, setUploadingLogo] = useState(false);

    const form = useForm<BrandingFormValues>({
        resolver: zodResolver(brandingFormSchema),
        defaultValues: {
            identity: {
                app_name: branding?.app_name || '',
            },
            contact_info: {
                support_email: branding?.contact_info?.support_email || '',
                phone: branding?.contact_info?.phone || '',
                address: branding?.contact_info?.address || '',
            },
            theme_config: {
                radius: branding?.theme_config?.radius || '0.5rem',
                light: branding?.theme_config?.light || {},
                dark: branding?.theme_config?.dark || {},
            },
        },
    });

    async function onSubmit(data: BrandingFormValues) {
        setLoading(true);
        setSaved(false);
        try {
            const updateData: UpdateBrandingDto = {
                identity: data.identity || null,
                contact_info: data.contact_info || null,
                theme_config: data.theme_config || null,
            };
            await onUpdateBranding(updateData);
            setSaved(true);
            setTimeout(() => setSaved(false), 2000);
        } catch (error) {
            console.error('Failed to update branding:', error);
        } finally {
            setLoading(false);
        }
    };

    function handleLogoChange(event: React.ChangeEvent<HTMLInputElement>) {
        const file = event.target.files?.[0];
        if (file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                alert('Please select an image file');
                return;
            }
            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('File size must be less than 5MB');
                return;
            }
            setLogoFile(file);
            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setLogoPreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    async function handleLogoUpload() {
        await onUploadLogo(logoFile!);
        setUploadingLogo(false);
    }

    function handleRemoveLogo() {
        setLogoFile(null);
        setLogoPreview(null);
    };

    return (
        <Card className="mt-6">
            <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                    <IconSettingsStar className="w-5 h-5" />
                    <span>Brand Configuration</span>
                </CardTitle>
                <CardDescription>
                    Customize your application's appearance and contact information
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                        <Tabs defaultValue="identity" className="w-full">
                            <TabsList className="grid w-full grid-cols-3">
                                <TabsTrigger value="identity">
                                    <IconIdBadge2 className="w-4 h-4 mr-2" />
                                    Identity
                                </TabsTrigger>
                                <TabsTrigger value="contact">
                                    <IconPhone className="w-4 h-4 mr-2" />
                                    Contact Info
                                </TabsTrigger>
                                <TabsTrigger value="theme">
                                    <IconPalette className="w-4 h-4 mr-2" />
                                    Theme Colors
                                </TabsTrigger>
                            </TabsList>
                            <TabsContent value="identity" className="space-y-4 pt-5">
                                <div className="space-y-6">
                                    <FormField
                                        control={form.control}
                                        name="identity.app_name"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="flex items-center space-x-2">
                                                    <IconIdBadge2 className="w-4 h-4" />
                                                    <span>Application Name</span>
                                                </FormLabel>
                                                <FormControl>
                                                    <Input
                                                        placeholder="My Awesome App"
                                                        {...field}
                                                    />
                                                </FormControl>
                                                <FormDescription>
                                                    Display name for your application
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <Separator />

                                    <div className="space-y-4">
                                        <div>
                                            <FormLabel className="flex items-center space-x-2 mb-3">
                                                <IconPhoto className="w-4 h-4" />
                                                <span>Logo</span>
                                            </FormLabel>
                                            <FormDescription className="mb-4">
                                                Upload your application logo (PNG or JPEG, max 5MB)
                                            </FormDescription>
                                        </div>

                                        {logoPreview ? (
                                            <div className="relative w-48 h-48 border-2 border-dashed rounded-lg p-4 flex items-center justify-center bg-muted/20">
                                                <img
                                                    src={logoPreview}
                                                    alt="Logo preview"
                                                    className="max-w-full max-h-full object-contain"
                                                />
                                                <Button
                                                    type="button"
                                                    variant="destructive"
                                                    size="icon"
                                                    className="absolute -top-2 -right-2 h-8 w-8 rounded-full"
                                                    onClick={handleRemoveLogo}
                                                >
                                                    <IconX className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        ) : (
                                            <div className="w-48 h-48 border-2 border-dashed rounded-lg p-4 flex items-center justify-center bg-muted/20">
                                                <div className="text-center">
                                                    <IconPhoto className="w-12 h-12 mx-auto text-muted-foreground mb-2" />
                                                    <p className="text-sm text-muted-foreground">No logo uploaded</p>
                                                </div>
                                            </div>
                                        )}

                                        <div className="flex items-center gap-2">
                                            <Input
                                                id="logo-upload"
                                                type="file"
                                                accept="image/png,image/jpeg"
                                                onChange={handleLogoChange}
                                                className="hidden"
                                            />
                                            <Button
                                                type="button"
                                                variant="outline"
                                                onClick={() => document.getElementById('logo-upload')?.click()}
                                                disabled={uploadingLogo}
                                            >
                                                <IconUpload className="mr-2 h-4 w-4" />
                                                Select Logo
                                            </Button>
                                            {logoFile && (
                                                <Button
                                                    type="button"
                                                    onClick={handleLogoUpload}
                                                    disabled={uploadingLogo}
                                                >
                                                    {uploadingLogo ? (
                                                        <>
                                                            <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />
                                                            Uploading...
                                                        </>
                                                    ) : (
                                                        <>
                                                            <IconUpload className="mr-2 h-4 w-4" />
                                                            Upload Logo
                                                        </>
                                                    )}
                                                </Button>
                                            )}
                                        </div>

                                        {logoFile && (
                                            <p className="text-sm text-muted-foreground">
                                                Selected: {logoFile.name} ({(logoFile.size / 1024).toFixed(2)} KB)
                                            </p>
                                        )}
                                    </div>
                                </div>
                            </TabsContent>
                            {/* Contact Information Tab */}
                            <TabsContent value="contact" className="space-y-4 pt-5">
                                <div className="space-y-4">
                                    <FormField
                                        control={form.control}
                                        name="contact_info.support_email"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="flex items-center space-x-2">
                                                    <IconMail className="w-4 h-4" />
                                                    <span>Support Email</span>
                                                </FormLabel>
                                                <FormControl>
                                                    <Input
                                                        type="email"
                                                        placeholder="support@example.com"
                                                        {...field}
                                                    />
                                                </FormControl>
                                                <FormDescription>
                                                    Primary contact email for customer support
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <FormField
                                        control={form.control}
                                        name="contact_info.phone"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="flex items-center space-x-2">
                                                    <IconPhone className="w-4 h-4" />
                                                    <span>Phone Number</span>
                                                </FormLabel>
                                                <FormControl>
                                                    <Input
                                                        placeholder="+1 (555) 123-4567"
                                                        {...field}
                                                    />
                                                </FormControl>
                                                <FormDescription>
                                                    Contact phone number
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <FormField
                                        control={form.control}
                                        name="contact_info.address"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel className="flex items-center space-x-2">
                                                    <IconMapPin className="w-4 h-4" />
                                                    <span>Address</span>
                                                </FormLabel>
                                                <FormControl>
                                                    <Input
                                                        placeholder="123 Main St, City, State ZIP"
                                                        {...field}
                                                    />
                                                </FormControl>
                                                <FormDescription>
                                                    Business address
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />
                                </div>
                            </TabsContent>

                            {/* Theme Configuration Tab */}
                            <TabsContent value="theme" className="space-y-4 pt-5">
                                <div className="space-y-6">
                                    <FormField
                                        control={form.control}
                                        name="theme_config.radius"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Border Radius</FormLabel>
                                                <FormControl>
                                                    <Input
                                                        placeholder="0.5rem"
                                                        {...field}
                                                    />
                                                </FormControl>
                                                <FormDescription>
                                                    Global border radius (e.g., 0.5rem, 8px)
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <Separator />

                                    {['light', 'dark'].map((mode) => (
                                        <div key={mode} className="space-y-4">
                                            <h3 className="text-lg font-medium capitalize">{mode} Mode</h3>

                                            {/* Core Colors */}
                                            <div className="grid grid-cols-1 md:grid-cols-2  gap-4">
                                                <ColorField control={form.control} name={`theme_config.${mode}.background`} label="Background" />
                                                <ColorField control={form.control} name={`theme_config.${mode}.foreground`} label="Foreground" />
                                                <ColorField control={form.control} name={`theme_config.${mode}.card`} label="Card" />
                                                <ColorField control={form.control} name={`theme_config.${mode}.card_foreground`} label="Card Foreground" />
                                                <ColorField control={form.control} name={`theme_config.${mode}.primary`} label="Primary" />
                                                <ColorField control={form.control} name={`theme_config.${mode}.primary_foreground`} label="Primary Foreground" />
                                            </div>

                                            {/* Sidebar Group */}

                                            <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Sidebar</h4>
                                            <div className="grid grid-cols-1 md:grid-cols-2  gap-4">
                                                <ColorField control={form.control} name={`theme_config.${mode}.sidebar`} label="Sidebar Bg" />
                                                <ColorField control={form.control} name={`theme_config.${mode}.sidebar_foreground`} label="Sidebar Text" />
                                                <ColorField control={form.control} name={`theme_config.${mode}.sidebar_primary`} label="Sidebar Primary" />
                                                <ColorField control={form.control} name={`theme_config.${mode}.sidebar_border`} label="Sidebar Border" />
                                            </div>


                                            {/* Charts Group */}
                                            <div className="space-y-2">
                                                <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Charts</h4>
                                                <div className="grid grid-cols-1 md:grid-cols-2  gap-2">
                                                    {[1, 2, 3, 4, 5].map((i) => (
                                                        <ColorField key={i} control={form.control} name={`theme_config.${mode}.chart_${i}`} label={`Chart ${i}`} />
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    ))}

                                </div>
                            </TabsContent>
                        </Tabs>

                        <div className="flex justify-end">
                            <Button type="submit" disabled={loading}>
                                {loading ? (
                                    <>
                                        <IconLoader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Saving...
                                    </>
                                ) : saved ? (
                                    <>
                                        <IconCheck className="mr-2 h-4 w-4" />
                                        Saved
                                    </>
                                ) : (
                                    'Save Changes'
                                )}
                            </Button>
                        </div>
                    </form>
                </Form>
            </CardContent>
        </Card>
    );
}

