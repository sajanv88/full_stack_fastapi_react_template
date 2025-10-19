import { StorageFormData, useSettings } from "@/components/providers/settings-provider";
import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Cloud, Database, Settings as SettingsIcon, CheckCircle, AlertCircle } from "lucide-react";
import { Loading } from "@/components/shared/loading";
import { useAuthContext } from "@/components/providers/auth-provider";
import { AvailableStorageProviderDto } from "@/api";


type StorageProvider = AvailableStorageProviderDto["provider"];


export function Settings() {
    const { storages, onConfigureStorage, loading } = useSettings();
    const { can } = useAuthContext();
    const canManageSettings = can('manage:storage_settings');
    const isAdminWithFullAccess = can('full:access');
    const [formData, setFormData] = useState<StorageFormData>({
        provider: 's3',
        is_enabled: false,
        region: '',
        aws_access_key: '',
        aws_secret_key: '',
        aws_bucket_name: '',
        azure_connection_string: '',
        azure_container_name: ''
    });
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('s3');

    // Get existing storage configuration for a provider
    const getStorageConfig = (provider: StorageProvider): AvailableStorageProviderDto | null => {
        return storages.find(s => s.provider === provider) || null;
    };


    // Update form data when switching tabs
    const handleTabChange = (provider: string) => {
        const storageProvider = provider as StorageProvider;
        setActiveTab(provider);
        const existingConfig = getStorageConfig(storageProvider);
        if (existingConfig) {
            setFormData({
                provider: existingConfig.provider,
                is_enabled: existingConfig.is_enabled,
                region: existingConfig.region,
                aws_access_key: existingConfig.aws_access_key || '',
                aws_secret_key: existingConfig.aws_secret_key || '',
                aws_bucket_name: existingConfig.aws_bucket_name || '',
                azure_connection_string: existingConfig.azure_connection_string || '',
                azure_container_name: existingConfig.azure_container_name || ''
            });
        } else {
            setFormData({
                provider: storageProvider,
                is_enabled: false,
                region: '',
                aws_access_key: '',
                aws_secret_key: '',
                aws_bucket_name: '',
                azure_connection_string: '',
                azure_container_name: ''
            });
        }
    };

    // Handle form submission
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            console.log("Form Data to be submitted:", formData);
            await onConfigureStorage(formData);
        } catch (error) {
            console.error('Failed to configure storage:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Update form field
    const updateField = (field: keyof StorageFormData, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    useEffect(() => {
        const provider = storages.find(s => s.is_enabled);
        if (provider) {
            setActiveTab(provider.provider);
            setFormData({
                provider: provider.provider,
                is_enabled: provider.is_enabled,
                region: provider.region,
                aws_access_key: provider.aws_access_key || '',
                aws_secret_key: provider.aws_secret_key || '',
                aws_bucket_name: provider.aws_bucket_name || '',
                azure_connection_string: provider.azure_connection_string || '',
                azure_container_name: provider.azure_container_name || ''
            });

        } else if (!provider && storages.length > 0) {
            const firstProvider = storages[0];
            setActiveTab(firstProvider.provider);
            const existingConfig = getStorageConfig(firstProvider.provider);
            if (existingConfig) {
                setFormData({
                    provider: existingConfig.provider,
                    is_enabled: existingConfig.is_enabled,
                    region: existingConfig.region,
                    aws_access_key: existingConfig.aws_access_key || '',
                    aws_secret_key: existingConfig.aws_secret_key || '',
                    aws_bucket_name: existingConfig.aws_bucket_name || '',
                    azure_connection_string: existingConfig.azure_connection_string || '',
                    azure_container_name: existingConfig.azure_container_name || ''
                });
            }
        }
    }, [storages]);

    if (!canManageSettings && !isAdminWithFullAccess) {
        return (
            <div className="grid place-items-center place-content-center h-40">
                <p>
                    You do not have permission to view this page.
                </p>
            </div>

        )
    }

    if (loading) {
        return (
            <div className="w-full md:max-w-4xl flex flex-col items-center justify-center min-h-[800px]">
                <h1 className="pb-5">Please wait settings are being fetched...</h1>
                <Loading variant="dots" size="lg" />
            </div>
        )
    }


    return (
        <div className="w-full xl:container xl:mx-auto xl:max-w-4xl">
            <div className="space-y-6">
                {/* Header */}
                <div className="flex items-center space-x-2">
                    <SettingsIcon className="h-8 w-8 text-primary" />
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">Storage Settings</h1>
                        <p className="text-muted-foreground text-sm">
                            Configure your cloud storage providers for file uploads and data storage
                        </p>
                    </div>
                </div>

                <Separator />

                {/* Storage Provider Tabs */}
                <Tabs value={activeTab} onValueChange={handleTabChange}>
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="s3" className="flex items-center space-x-2">
                            <Cloud className="h-4 w-4" />
                            <span>AWS S3</span>
                            {getStorageConfig('s3')?.is_enabled && (
                                <CheckCircle className="h-4 w-4 text-green-500" />
                            )}
                        </TabsTrigger>
                        <TabsTrigger value="azure_blob" className="flex items-center space-x-2">
                            <Database className="h-4 w-4" />
                            <span>Azure Blob</span>
                            {getStorageConfig('azure_blob')?.is_enabled && (
                                <CheckCircle className="h-4 w-4 text-green-500" />
                            )}
                        </TabsTrigger>
                    </TabsList>

                    {/* AWS S3 Configuration */}
                    <TabsContent value="s3" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <Cloud className="h-5 w-5 text-orange-500" />
                                    <span>Amazon S3 Configuration</span>
                                    {getStorageConfig('s3')?.is_enabled && (
                                        <Badge variant="secondary" className="ml-2">
                                            <CheckCircle className="h-3 w-3 mr-1" />
                                            Active
                                        </Badge>
                                    )}
                                </CardTitle>
                                <CardDescription>
                                    Configure your Amazon S3 bucket for file storage and uploads
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <form onSubmit={handleSubmit} className="space-y-6">
                                    {/* Enable/Disable Toggle */}
                                    <div className="flex items-center justify-between p-4 border rounded-lg">
                                        <div className="space-y-0.5">
                                            <Label className="text-base font-medium">Enable S3 Storage</Label>
                                            <p className="text-sm text-muted-foreground">
                                                Activate Amazon S3 for file storage operations
                                            </p>
                                        </div>
                                        <Switch
                                            checked={formData.is_enabled}
                                            onCheckedChange={(checked) => updateField('is_enabled', checked)}
                                        />
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {/* Region */}
                                        <div className="space-y-2">
                                            <Label htmlFor="region">AWS Region</Label>
                                            <Select
                                                key={formData?.region}
                                                defaultValue={formData?.region}
                                                onValueChange={(value) => updateField('region', value)}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select AWS region" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="us-east-1">US East (N. Virginia)</SelectItem>
                                                    <SelectItem value="us-west-2">US West (Oregon)</SelectItem>
                                                    <SelectItem value="eu-west-1">Europe (Ireland)</SelectItem>
                                                    <SelectItem value="eu-central-1">Europe (Frankfurt)</SelectItem>
                                                    <SelectItem value="ap-southeast-1">Asia Pacific (Singapore)</SelectItem>
                                                    <SelectItem value="ap-northeast-1">Asia Pacific (Tokyo)</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        {/* Bucket Name */}
                                        <div className="space-y-2">
                                            <Label htmlFor="bucket">Bucket Name</Label>
                                            <Input
                                                id="bucket"
                                                type="text"
                                                placeholder="my-app-bucket"
                                                value={formData.aws_bucket_name || ''}
                                                onChange={(e) => updateField('aws_bucket_name', e.target.value)}
                                            />
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {/* Access Key */}
                                        <div className="space-y-2">
                                            <Label htmlFor="access-key">Access Key ID</Label>
                                            <Input
                                                id="access-key"
                                                type="text"
                                                placeholder="AKIA..."
                                                value={formData.aws_access_key || ''}
                                                onChange={(e) => updateField('aws_access_key', e.target.value)}
                                            />
                                        </div>

                                        {/* Secret Key */}
                                        <div className="space-y-2">
                                            <Label htmlFor="secret-key">Secret Access Key</Label>
                                            <Input
                                                id="secret-key"
                                                type="password"
                                                placeholder="••••••••••••••••"
                                                value={formData.aws_secret_key || ''}
                                                onChange={(e) => updateField('aws_secret_key', e.target.value)}
                                            />
                                        </div>
                                    </div>

                                    <Alert>
                                        <AlertCircle className="h-4 w-4" />
                                        <AlertDescription>
                                            Ensure your AWS credentials have the necessary S3 permissions for your bucket operations.
                                        </AlertDescription>
                                    </Alert>

                                    <Button
                                        type="submit"
                                        disabled={isLoading}
                                        className="w-full"
                                    >
                                        {isLoading ? 'Saving...' : 'Save S3 Configuration'}
                                    </Button>
                                </form>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    {/* Azure Blob Storage Configuration */}
                    <TabsContent value="azure_blob" className="space-y-4">
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center space-x-2">
                                    <Database className="h-5 w-5 text-blue-500" />
                                    <span>Azure Blob Storage Configuration</span>
                                    {getStorageConfig('azure_blob')?.is_enabled && (
                                        <Badge variant="secondary" className="ml-2">
                                            <CheckCircle className="h-3 w-3 mr-1" />
                                            Active
                                        </Badge>
                                    )}
                                </CardTitle>
                                <CardDescription>
                                    Configure your Azure Blob Storage container for file storage and uploads
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <form onSubmit={handleSubmit} className="space-y-6">
                                    {/* Enable/Disable Toggle */}
                                    <div className="flex items-center justify-between p-4 border rounded-lg">
                                        <div className="space-y-0.5">
                                            <Label className="text-base font-medium">Enable Azure Blob Storage</Label>
                                            <p className="text-sm text-muted-foreground">
                                                Activate Azure Blob Storage for file storage operations
                                            </p>
                                        </div>
                                        <Switch
                                            checked={formData.is_enabled}
                                            onCheckedChange={(checked) => updateField('is_enabled', checked)}
                                        />
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {/* Region */}
                                        <div className="space-y-2">
                                            <Label htmlFor="azure-region">Azure Region</Label>
                                            <Select
                                                value={formData.region}
                                                onValueChange={(value) => updateField('region', value)}
                                            >
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select Azure region" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="eastus">East US</SelectItem>
                                                    <SelectItem value="westus2">West US 2</SelectItem>
                                                    <SelectItem value="centralus">Central US</SelectItem>
                                                    <SelectItem value="westeurope">West Europe</SelectItem>
                                                    <SelectItem value="northeurope">North Europe</SelectItem>
                                                    <SelectItem value="southeastasia">Southeast Asia</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        {/* Container Name */}
                                        <div className="space-y-2">
                                            <Label htmlFor="container">Container Name</Label>
                                            <Input
                                                id="container"
                                                type="text"
                                                placeholder="my-app-container"
                                                value={formData.azure_container_name || ''}
                                                onChange={(e) => updateField('azure_container_name', e.target.value)}
                                            />
                                        </div>
                                    </div>

                                    {/* Connection String */}
                                    <div className="space-y-2">
                                        <Label htmlFor="connection-string">Connection String</Label>
                                        <Input
                                            id="connection-string"
                                            type="password"
                                            placeholder="DefaultEndpointsProtocol=https;AccountName=..."
                                            value={formData.azure_connection_string || ''}
                                            onChange={(e) => updateField('azure_connection_string', e.target.value)}
                                        />
                                        <p className="text-xs text-muted-foreground">
                                            You can find this in your Azure Storage Account's Access Keys section
                                        </p>
                                    </div>

                                    <Alert>
                                        <AlertCircle className="h-4 w-4" />
                                        <AlertDescription>
                                            Ensure your Azure Storage Account has the necessary permissions and the container exists.
                                        </AlertDescription>
                                    </Alert>

                                    <Button
                                        type="submit"
                                        disabled={isLoading}
                                        className="w-full"
                                    >
                                        {isLoading ? 'Saving...' : 'Save Azure Configuration'}
                                    </Button>
                                </form>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>

                {/* Storage Status Overview */}
                <Card>
                    <CardHeader>
                        <CardTitle>Storage Providers Status</CardTitle>
                        <CardDescription>
                            Overview of your configured storage providers
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* AWS S3 Status */}
                            <div className="flex items-center justify-between p-4 border rounded-lg">
                                <div className="flex items-center space-x-3">
                                    <Cloud className="h-8 w-8 text-orange-500" />
                                    <div>
                                        <p className="font-medium">Amazon S3</p>
                                        <p className="text-sm text-muted-foreground">
                                            {getStorageConfig('s3')?.region || 'Not configured'}
                                        </p>
                                    </div>
                                </div>
                                <Badge variant={getStorageConfig('s3')?.is_enabled ? 'default' : 'secondary'}>
                                    {getStorageConfig('s3')?.is_enabled ? 'Active' : 'Inactive'}
                                </Badge>
                            </div>

                            {/* Azure Blob Status */}
                            <div className="flex items-center justify-between p-4 border rounded-lg">
                                <div className="flex items-center space-x-3">
                                    <Database className="h-8 w-8 text-blue-500" />
                                    <div>
                                        <p className="font-medium">Azure Blob Storage</p>
                                        <p className="text-sm text-muted-foreground">
                                            {getStorageConfig('azure_blob')?.region || 'Not configured'}
                                        </p>
                                    </div>
                                </div>
                                <Badge variant={getStorageConfig('azure_blob')?.is_enabled ? 'default' : 'secondary'}>
                                    {getStorageConfig('azure_blob')?.is_enabled ? 'Active' : 'Inactive'}
                                </Badge>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}