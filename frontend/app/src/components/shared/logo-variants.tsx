import { cn } from '@/lib/utils'

interface LogoProps {
    className?: string
    size?: 'sm' | 'md' | 'lg'
    showText?: boolean
    variant?: 'default' | 'compact' | 'icon-only'
}

export function Logo({ className, size = 'md', showText = true, variant = 'default' }: LogoProps) {
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

    if (variant === 'icon-only') {
        return (
            <div className={cn(
                'relative flex items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 via-purple-500 to-teal-500 shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105',
                sizeClasses[size],
                className
            )}>
                <div className="absolute inset-2 rounded-lg bg-white/20 backdrop-blur-sm">
                    <div className="h-full w-full rounded-lg border border-white/30 flex items-center justify-center">
                        <div className="text-white font-bold text-xs md:text-sm lg:text-base">
                            FS
                        </div>
                    </div>
                </div>
                <div className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-green-400 animate-pulse shadow-lg shadow-green-400/50"></div>
                <div className="absolute -bottom-1 -left-1 h-1.5 w-1.5 rounded-full bg-orange-400 animate-pulse delay-500 shadow-lg shadow-orange-400/50"></div>
            </div>
        )
    }

    if (variant === 'compact') {
        return (
            <div className={cn('flex items-center gap-2', className)}>
                <div className={cn(
                    'relative flex items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-teal-500 shadow-md',
                    size === 'sm' ? 'h-6 w-6' : size === 'md' ? 'h-8 w-8' : 'h-10 w-10'
                )}>
                    <div className="text-white font-bold text-xs">FS</div>
                </div>
                {showText && (
                    <span className={cn(
                        'font-semibold text-gray-800 dark:text-white',
                        size === 'sm' ? 'text-sm' : size === 'md' ? 'text-base' : 'text-lg'
                    )}>
                        Full Stack
                    </span>
                )}
            </div>
        )
    }

    return (
        <div className={cn('flex items-center gap-3', className)}>
            {/* Modern geometric logo */}
            <div className={cn(
                'relative flex items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 via-purple-500 to-teal-500 shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105 group',
                sizeClasses[size]
            )}>
                {/* Inner geometric shape */}
                <div className="absolute inset-2 rounded-lg bg-white/20 backdrop-blur-sm group-hover:bg-white/30 transition-all duration-300">
                    <div className="h-full w-full rounded-lg border border-white/30 flex items-center justify-center">
                        {/* Logo symbol - stylized "FS" for Full Stack */}
                        <div className="text-white font-bold text-xs md:text-sm lg:text-base group-hover:scale-110 transition-transform duration-300">
                            FS
                        </div>
                    </div>
                </div>

                {/* Animated corner dots */}
                <div className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-green-400 animate-pulse shadow-lg shadow-green-400/50"></div>
                <div className="absolute -bottom-1 -left-1 h-1.5 w-1.5 rounded-full bg-orange-400 animate-pulse delay-500 shadow-lg shadow-orange-400/50"></div>

                {/* Rotating border effect */}
                <div className="absolute inset-0 rounded-xl border-2 border-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-teal-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300 animate-spin-slow"></div>
            </div>

            {/* Text content */}
            {showText && (
                <div className="flex flex-col">
                    <span className={cn(
                        'font-bold bg-gradient-to-r from-gray-900 via-purple-700 to-blue-600 bg-clip-text text-transparent dark:from-white dark:via-purple-300 dark:to-blue-300 hover:from-purple-600 hover:to-teal-600 transition-all duration-300',
                        textSizeClasses[size]
                    )}>
                        Full Stack
                    </span>
                    <span className={cn(
                        'text-muted-foreground font-medium tracking-wide opacity-75 hover:opacity-100 transition-opacity duration-200',
                        size === 'sm' ? 'text-[10px]' : size === 'lg' ? 'text-sm' : 'text-xs'
                    )}>
                        FastAPI • React • Modern
                    </span>
                </div>
            )}
        </div>
    )
}

// Alternative simple version without dependencies
export function SimpleLogo({ className = '', size = 'md' }: { className?: string, size?: 'sm' | 'md' | 'lg' }) {
    const logoSize = size === 'sm' ? 'h-8 w-8' : size === 'md' ? 'h-12 w-12' : 'h-16 w-16'
    const textSize = size === 'sm' ? 'text-sm' : size === 'md' ? 'text-lg' : 'text-xl'

    return (
        <div className={`flex items-center gap-3 ${className}`}>
            <div className={`${logoSize} bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl shadow-lg flex items-center justify-center`}>
                <span className="text-white font-bold">FS</span>
            </div>
            <div className="flex flex-col">
                <span className={`${textSize} font-bold text-gray-800 dark:text-white`}>
                    Full Stack
                </span>
                <span className="text-xs text-gray-600 dark:text-gray-400">
                    FastAPI • React
                </span>
            </div>
        </div>
    )
}
