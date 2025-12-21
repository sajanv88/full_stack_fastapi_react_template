import { cn } from '@/lib/utils'
import { useAppConfig } from '../providers/app-config-provider'

interface LogoProps {
    className?: string
    size?: 'sm' | 'md' | 'lg'
    showText?: boolean
}

export function Logo({ className, size = 'md', showText = true }: LogoProps) {
    const { branding } = useAppConfig();
    const sizeClasses = {
        sm: 'h-8 w-8',
        md: 'h-12 w-12',
        lg: 'h-16 w-16'
    }

    const textSizeClasses = {
        sm: 'text-sm',
        md: 'text-lg',
        lg: 'text-xl'
    }
    if (branding?.logo_url) {
        return (
            <div className={cn('flex items-center gap-3', className)}>
                <img
                    src={branding.logo_url}
                    alt={branding.app_name || 'Logo'}
                    className={cn(
                        'object-contain rounded-lg',
                        sizeClasses[size]
                    )}
                />
                {showText && branding.app_name && (
                    <span className={cn(
                        'font-bold text-foreground',
                        textSizeClasses[size]
                    )}>
                        {branding.app_name}
                    </span>
                )}
            </div>
        )
    }
    return (
        <div className={cn('flex items-center gap-3', className)}>
            {/* Modern geometric logo */}
            <div className={cn(
                'relative flex items-center justify-center rounded-xl bg-linear-to-br from-blue-500 via-purple-500 to-teal-500 shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105',
                sizeClasses[size]
            )}>
                {/* Inner geometric shape */}
                <div className="absolute inset-2 rounded-lg bg-white/20 backdrop-blur-sm">
                    <div className="h-full w-full rounded-lg border border-white/30 flex items-center justify-center">
                        {/* Logo symbol - stylized "FS" for Full Stack */}
                        <div className="text-white font-bold text-xs md:text-sm lg:text-base">
                            FS
                        </div>
                    </div>
                </div>

                {/* Subtle animation dots */}
                <div className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-green-400 animate-pulse shadow-lg shadow-green-400/50"></div>
                <div className="absolute -bottom-1 -left-1 h-1.5 w-1.5 rounded-full bg-orange-400 animate-pulse delay-500 shadow-lg shadow-orange-400/50"></div>
            </div>

            {/* Text content */}
            {showText && (
                <div className="flex flex-col">
                    <span className={cn(
                        'font-bold bg-linear-to-r from-gray-900 via-purple-700 to-blue-600 bg-clip-text text-transparent dark:from-white dark:via-purple-300 dark:to-blue-300',
                        textSizeClasses[size]
                    )}>
                        Full Stack
                    </span>
                    <span className={cn(
                        'text-xs text-muted-foreground font-medium tracking-wide',
                        size === 'sm' ? 'text-[10px]' : size === 'lg' ? 'text-sm' : 'text-xs'
                    )}>
                        FastAPI • React
                    </span>
                </div>
            )}
        </div>
    )
}