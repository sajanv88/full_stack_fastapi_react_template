import React, { useState, useRef, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from '@/components/ui/form'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import {
    User,
    Mail,
    Camera,
    Save,
    Upload,
    CheckCircle,
    AlertCircle,
    UserCircle,
    Shield,
    Calendar,
    Edit3,
    X
} from 'lucide-react'
import { useAuthContext } from '@/components/providers/auth-provider'
import { toast } from 'sonner'
import { getAccessToken } from '@/lib/utils'

// Form validation schema
const profileSchema = z.object({
    first_name: z.string().min(1, 'First name is required').min(2, 'First name must be at least 2 characters'),
    last_name: z.string().min(1, 'Last name is required').min(2, 'Last name must be at least 2 characters'),
    gender: z.enum(['male', 'female', 'other', 'prefer_not_to_say']),
})

type ProfileFormData = z.infer<typeof profileSchema>

export function Profile() {
    const { user, onUpdateProfile } = useAuthContext()

    const [isEditing, setIsEditing] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [uploadingImage, setUploadingImage] = useState(false)
    const [imagePreview, setImagePreview] = useState<string | null>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)
    console.log(user, "user");
    const form = useForm<ProfileFormData>({
        resolver: zodResolver(profileSchema),
        defaultValues: {
            first_name: '',
            last_name: '',
            gender: 'prefer_not_to_say',
        },
    })

    // Update form values when user data is available or when entering edit mode
    useEffect(() => {
        if (user) {
            form.reset({
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                gender: (user.gender as any) || 'prefer_not_to_say',
            })
        }
    }, [user, form])

    // Reset form values when entering edit mode
    useEffect(() => {
        if (isEditing && user) {
            form.reset({
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                gender: (user.gender as any) || 'prefer_not_to_say',
            })
        }
    }, [isEditing, user, form])

    const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0]
        if (!file) return

        // Validate file type
        if (!file.type.startsWith('image/')) {
            toast.error('Please select a valid image file')
            return
        }

        // Validate file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
            toast.error('Image size should be less than 5MB')
            return
        }

        // Show preview
        const reader = new FileReader()
        reader.onload = (e) => {
            setImagePreview(e.target?.result as string)
        }
        reader.readAsDataURL(file)

        // Upload image
        setUploadingImage(true)
        try {
            const formData = new FormData()
            formData.append('file', file)

            const accessToken = getAccessToken()
            // TODO: Implement image upload API endpoint
            // const apiClient = new ApiClient({
            //     HEADERS: {
            //         Authorization: `Bearer ${accessToken}`
            //     }
            // })
            // const response = await apiClient.users.uploadProfileImageApiV1UsersProfileImagePost({ formData })

            console.log('Image upload ready for API implementation', { accessToken, formData })
            toast.success('Profile image updated successfully!')
        } catch (error) {
            console.error('Error uploading image:', error)
            toast.error('Failed to upload image')
            setImagePreview(null)
        } finally {
            setUploadingImage(false)
        }
    }

    const onSubmit = async (data: ProfileFormData) => {
        if (!user) return

        setIsLoading(true)
        await onUpdateProfile({
            firstName: data.first_name,
            lastName: data.last_name,
            gender: data.gender,
            imageUrl: imagePreview
        });
        setIsLoading(false);

    }

    const getGenderDisplay = (gender: string) => {
        const genderMap = {
            'male': 'Male',
            'female': 'Female',
            'other': 'Other',
            'prefer_not_to_say': 'Prefer not to say'
        }
        return genderMap[gender as keyof typeof genderMap] || 'Not specified'
    }

    const getUserInitials = (firstName?: string, lastName?: string) => {
        return `${firstName?.charAt(0) || ''}${lastName?.charAt(0) || ''}`.toUpperCase()
    }

    if (!user) {
        return (
            <div className="px-4 py-8">
                <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                        Please log in to view your profile.
                    </AlertDescription>
                </Alert>
            </div>
        )
    }

    return (
        <div className="px-4 py-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 space-y-4 sm:space-y-0">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold">Profile Settings</h1>
                    <p className="text-muted-foreground">Manage your account information and preferences</p>
                </div>

                {!isEditing ? (
                    <Button onClick={() => setIsEditing(true)} className="w-full sm:w-auto">
                        <Edit3 className="w-4 h-4 mr-2" />
                        Edit Profile
                    </Button>
                ) : (
                    <Button
                        variant="outline"
                        onClick={() => {
                            setIsEditing(false)
                            setImagePreview(null)
                            form.reset()
                        }}
                        className="w-full sm:w-auto"
                    >
                        <X className="w-4 h-4 mr-2" />
                        Cancel
                    </Button>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Profile Image Card */}
                <Card className="lg:col-span-1">
                    <CardHeader className="text-center">
                        <CardTitle className="flex items-center justify-center space-x-2">
                            <UserCircle className="w-5 h-5" />
                            <span>Profile Picture</span>
                        </CardTitle>
                        <CardDescription>
                            {isEditing ? 'Click to upload a new image' : 'Your profile image'}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="text-center space-y-4">
                        <div className="relative inline-block">
                            <Avatar className="w-32 h-32 mx-auto border-4 border-muted">
                                <AvatarImage
                                    src={imagePreview || user.image_url || ''}
                                    alt={`${user.first_name} ${user.last_name}`}
                                />
                                <AvatarFallback className="text-2xl">
                                    {getUserInitials(user.first_name, user.last_name)}
                                </AvatarFallback>
                            </Avatar>

                            {isEditing && (
                                <Button
                                    size="sm"
                                    className="absolute bottom-0 right-0 rounded-full"
                                    onClick={() => fileInputRef.current?.click()}
                                    disabled={uploadingImage}
                                >
                                    {uploadingImage ? (
                                        <Upload className="w-4 h-4 animate-spin" />
                                    ) : (
                                        <Camera className="w-4 h-4" />
                                    )}
                                </Button>
                            )}
                        </div>

                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleImageUpload}
                            className="hidden"
                            aria-label="Upload profile picture"
                        />

                        {isEditing && (
                            <div className="text-xs text-muted-foreground space-y-1">
                                <p>JPG, PNG or GIF (max. 5MB)</p>
                                <p>Recommended: 400x400px</p>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Profile Information Card */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            <User className="w-5 h-5" />
                            <span>Personal Information</span>
                        </CardTitle>
                        <CardDescription>
                            {isEditing ? 'Update your personal details' : 'Your account information'}
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {isEditing ? (
                            <Form {...form}>
                                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                        <FormField
                                            control={form.control}
                                            name="first_name"
                                            render={({ field }) => (
                                                <FormItem>
                                                    <FormLabel>First Name</FormLabel>
                                                    <FormControl>
                                                        <Input placeholder="Enter your first name" {...field} />
                                                    </FormControl>
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />

                                        <FormField
                                            control={form.control}
                                            name="last_name"
                                            render={({ field }) => (
                                                <FormItem>
                                                    <FormLabel>Last Name</FormLabel>
                                                    <FormControl>
                                                        <Input placeholder="Enter your last name" {...field} />
                                                    </FormControl>
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />
                                    </div>



                                    <FormField
                                        control={form.control}
                                        name="gender"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Gender</FormLabel>
                                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                                    <FormControl>
                                                        <SelectTrigger>
                                                            <SelectValue placeholder="Select your gender" />
                                                        </SelectTrigger>
                                                    </FormControl>
                                                    <SelectContent>
                                                        <SelectItem value="male">Male</SelectItem>
                                                        <SelectItem value="female">Female</SelectItem>
                                                        <SelectItem value="other">Other</SelectItem>
                                                        <SelectItem value="prefer_not_to_say">Prefer not to say</SelectItem>
                                                    </SelectContent>
                                                </Select>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
                                        <Button type="submit" disabled={isLoading} className="flex-1">
                                            {isLoading ? (
                                                <>
                                                    <Upload className="w-4 h-4 mr-2 animate-spin" />
                                                    Saving...
                                                </>
                                            ) : (
                                                <>
                                                    <Save className="w-4 h-4 mr-2" />
                                                    Save Changes
                                                </>
                                            )}
                                        </Button>
                                        <Button
                                            type="button"
                                            variant="outline"
                                            onClick={() => {
                                                setIsEditing(false)
                                                setImagePreview(null)
                                                form.reset()
                                            }}
                                            className="flex-1"
                                        >
                                            Cancel
                                        </Button>
                                    </div>
                                </form>
                            </Form>
                        ) : (
                            <div className="space-y-6">
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                    <div className="space-y-2">
                                        <Label className="text-sm font-medium text-muted-foreground">First Name</Label>
                                        <p className="text-lg font-medium">{user.first_name}</p>
                                    </div>
                                    <div className="space-y-2">
                                        <Label className="text-sm font-medium text-muted-foreground">Last Name</Label>
                                        <p className="text-lg font-medium">{user.last_name}</p>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-sm font-medium text-muted-foreground flex items-center space-x-2">
                                        <Mail className="w-4 h-4" />
                                        <span>Email Address</span>
                                    </Label>
                                    <p className="text-lg">{user.email}</p>
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-sm font-medium text-muted-foreground">Gender</Label>
                                    <p className="text-lg">{getGenderDisplay(user.gender)}</p>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Account Status Card */}
            <Card className="mt-6">
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <Shield className="w-5 h-5" />
                        <span>Account Status</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="space-y-2">
                            <Label className="text-sm font-medium text-muted-foreground">Account Status</Label>
                            <div className="flex items-center space-x-2">
                                {user.is_active ? (
                                    <>
                                        <CheckCircle className="w-4 h-4 text-green-500" />
                                        <Badge variant="secondary" className="bg-green-100 text-green-800">
                                            Active
                                        </Badge>
                                    </>
                                ) : (
                                    <>
                                        <AlertCircle className="w-4 h-4 text-red-500" />
                                        <Badge variant="destructive">Inactive</Badge>
                                    </>
                                )}
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label className="text-sm font-medium text-muted-foreground">Role</Label>
                            <Badge variant="outline" className="w-fit">
                                {user.role?.name || 'No role assigned'}
                            </Badge>
                        </div>

                        <div className="space-y-2">
                            <Label className="text-sm font-medium text-muted-foreground flex items-center space-x-2">
                                <Calendar className="w-4 h-4" />
                                <span>Activated</span>
                            </Label>
                            <p className="text-sm">
                                {user.activated_at
                                    ? new Date(user.activated_at).toLocaleDateString()
                                    : 'Not activated'
                                }
                            </p>
                        </div>

                        <div className="space-y-2">
                            <Label className="text-sm font-medium text-muted-foreground">User ID</Label>
                            <p className="text-xs font-mono bg-muted px-2 py-1 rounded">
                                {user.id}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
