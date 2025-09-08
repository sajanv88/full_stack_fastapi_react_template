import { useState, useEffect, useRef } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { X, Loader2 } from 'lucide-react'
import { ApiClient, Tenant } from '@/api'
import { toast } from 'sonner'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { getTenant, setTenant } from '@/lib/utils'

interface TenantSearchProps {
    onTenantSelect?: (tenant: Tenant | null) => void
    placeholder?: string
    className?: string
}

export function TenantSelection({
    onTenantSelect,
    placeholder = "Search tenant by name...",
    className
}: TenantSearchProps) {
    const [isLoading, setIsLoading] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const [debouncedQuery, setDebouncedQuery] = useState('')
    const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null)

    useEffect(() => {
        const tenant = getTenant();
        if (tenant) {
            setSearchQuery(tenant.name);
            onTenantSelect?.(tenant);
        }
    }, [])

    // Debounce search query
    useEffect(() => {
        if (searchTimeoutRef.current) {
            clearTimeout(searchTimeoutRef.current)
        }

        searchTimeoutRef.current = setTimeout(() => {
            setDebouncedQuery(searchQuery)
        }, 300)

        return () => {
            if (searchTimeoutRef.current) {
                clearTimeout(searchTimeoutRef.current)
            }
        }
    }, [searchQuery])

    // Search tenants when debounced query changes
    useEffect(() => {
        if (debouncedQuery.length >= 2) {
            searchTenants(debouncedQuery)
        }
    }, [debouncedQuery])

    const searchTenants = async (query: string) => {
        setIsLoading(true)
        try {
            const apiClient = new ApiClient()
            const response = await apiClient.tenants.searchTenantByNameApiV1TenantsSearchByNameGet({
                name: query
            })


            if (response) {
                setSearchQuery(response.name)
                setTenant(response)
                onTenantSelect?.(response)
            } else {
                onTenantSelect?.(null)
                setTenant(null)
            }
        } catch (error) {
            console.error('Error searching tenants:', error)
            toast.error('Failed to search tenant', {
                richColors: true
            })
            onTenantSelect?.(null)
            setTenant(null)
        } finally {
            setIsLoading(false)
        }
    }

    const clearSelection = () => {
        setSearchQuery('')
        onTenantSelect?.(null)
        setTenant(null)
    }

    return (
        <Card className="w-full max-w-md shadow-lg mb-5">
            <CardHeader>
                <CardTitle>
                    Select Tenant
                </CardTitle>
                <CardDescription>
                    Please enter the tenant name to search.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className={`relative ${className || ''}`}>
                    <Input
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder={placeholder}
                        className="pr-20"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                        {isLoading && (
                            <Loader2 className="w-4 h-4 animate-spin text-muted-foreground mr-2" />
                        )}
                        {searchQuery && (
                            <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={clearSelection}
                                className="h-auto p-1"
                            >
                                <X className="w-4 h-4" />
                            </Button>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    )
}