import { useState, useEffect, useRef } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { X, Loader2 } from 'lucide-react'
import { TenantDto } from '@/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cn, getApiClient, getTenant, setTenant } from '@/lib/utils'
import { useAppConfig } from '@/components/providers/app-config-provider'

interface TenantSearchProps {
    onTenantSelect?: (tenant: TenantDto | null) => void
    placeholder?: string
    className?: string
}

export function TenantSelection({
    onTenantSelect,
    placeholder = "Search tenant by name...",
    className
}: TenantSearchProps) {
    const { redirectToTenantDomain } = useAppConfig()
    const [isLoading, setIsLoading] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')
    const [debouncedQuery, setDebouncedQuery] = useState('')
    const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null)
    const [error, setError] = useState<string | null>(null)
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
        setError(null)

        setIsLoading(true)
        try {
            const apiClient = getApiClient()
            const response = await apiClient.tenants.searchByNameApiV1TenantsSearchByNameNameGet({
                name: query
            })


            if (response) {
                setSearchQuery(response.name)
                setTenant(response)
                onTenantSelect?.(response)
                redirectToTenantDomain(response)
            } else {
                onTenantSelect?.(null)
                setTenant(null)
            }
        } catch (error) {
            setError("We can't find the tenant you're looking for. Please check the name and try again.")
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
        setError(null)
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
                        className={cn("pr-20", error && "border-red-500")}
                    />

                    <div className="absolute top-[5px] right-0 flex items-center pr-3">
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
                    {error && (
                        <span className="inline-flex pt-4   text-sm text-red-500">{error}</span>
                    )}
                </div>
            </CardContent>
        </Card>
    )
}