import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
    Github,
    Twitter,
    Linkedin,
    Mail,
    Heart,
    Code,
    Zap,
    Shield,
    Globe,
    ExternalLink,
    Coffee
} from 'lucide-react'

export function Footer() {
    const currentYear = new Date().getFullYear()

    const footerLinks = {
        product: [
            { name: 'Features', href: '#' },
            { name: 'Documentation', href: '#' },
            { name: 'API Reference', href: '#' },
            { name: 'Changelog', href: '#' }
        ],
        company: [
            { name: 'About', href: '#' },
            { name: 'Blog', href: '#' },
            { name: 'Careers', href: '#' },
            { name: 'Contact', href: '#' }
        ],
        support: [
            { name: 'Help Center', href: '#' },
            { name: 'Community', href: '#' },
            { name: 'Status', href: '#' },
            { name: 'Security', href: '#' }
        ],
        legal: [
            { name: 'Privacy Policy', href: '#' },
            { name: 'Terms of Service', href: '#' },
            { name: 'Cookie Policy', href: '#' },
            { name: 'License', href: '#' }
        ]
    }

    const socialLinks = [
        { name: 'GitHub', icon: Github, href: 'https://github.com', color: 'hover:text-gray-900 dark:hover:text-gray-100' },
        { name: 'Twitter', icon: Twitter, href: 'https://twitter.com', color: 'hover:text-blue-500' },
        { name: 'LinkedIn', icon: Linkedin, href: 'https://linkedin.com', color: 'hover:text-blue-600' },
        { name: 'Email', icon: Mail, href: 'mailto:contact@example.com', color: 'hover:text-red-500' }
    ]

    const techStack = [
        { name: 'React', icon: Code },
        { name: 'TypeScript', icon: Zap },
        { name: 'FastAPI', icon: Shield },
        { name: 'Tailwind', icon: Globe }
    ]

    return (
        <footer className="bg-background border-t border-border">
            <div className="container mx-auto px-4 py-8 sm:py-12">
                {/* Main Footer Content */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-12">
                    {/* Brand Section */}
                    <div className="lg:col-span-2 space-y-4">
                        <div className="flex items-center space-x-2">
                            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
                                <Zap className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h3 className="text-lg font-bold">FullStack Template</h3>
                                <p className="text-sm text-muted-foreground">FastAPI + React</p>
                            </div>
                        </div>

                        <p className="text-muted-foreground text-sm leading-relaxed max-w-md">
                            A modern full-stack application template built with FastAPI backend and React frontend.
                            Featuring AI integration, authentication, and responsive design.
                        </p>

                        {/* Tech Stack */}
                        <div className="space-y-3">
                            <p className="text-sm font-medium text-muted-foreground">Built with</p>
                            <div className="flex flex-wrap gap-2">
                                {techStack.map((tech) => (
                                    <Badge key={tech.name} variant="secondary" className="flex items-center space-x-1">
                                        <tech.icon className="w-3 h-3" />
                                        <span className="text-xs">{tech.name}</span>
                                    </Badge>
                                ))}
                            </div>
                        </div>

                        {/* Social Links */}
                        <div className="flex space-x-4">
                            {socialLinks.map((social) => (
                                <Button
                                    key={social.name}
                                    variant="ghost"
                                    size="sm"
                                    asChild
                                    className={`p-2 ${social.color} transition-colors`}
                                >
                                    <a
                                        href={social.href}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        aria-label={social.name}
                                    >
                                        <social.icon className="w-4 h-4" />
                                    </a>
                                </Button>
                            ))}
                        </div>
                    </div>

                    {/* Product Links */}
                    <div className="space-y-4">
                        <h4 className="font-semibold text-sm">Product</h4>
                        <ul className="space-y-2">
                            {footerLinks.product.map((link) => (
                                <li key={link.name}>
                                    <a
                                        href={link.href}
                                        className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center"
                                    >
                                        {link.name}
                                        <ExternalLink className="w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Company Links */}
                    <div className="space-y-4">
                        <h4 className="font-semibold text-sm">Company</h4>
                        <ul className="space-y-2">
                            {footerLinks.company.map((link) => (
                                <li key={link.name}>
                                    <a
                                        href={link.href}
                                        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                                    >
                                        {link.name}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Support Links */}
                    <div className="space-y-4">
                        <h4 className="font-semibold text-sm">Support</h4>
                        <ul className="space-y-2">
                            {footerLinks.support.map((link) => (
                                <li key={link.name}>
                                    <a
                                        href={link.href}
                                        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                                    >
                                        {link.name}
                                    </a>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                <Separator className="my-8" />

                {/* Bottom Section */}
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                        <p className="text-sm text-muted-foreground">
                            © {currentYear} FullStack Template. All rights reserved.
                        </p>
                        <div className="flex space-x-4">
                            {footerLinks.legal.map((link) => (
                                <a
                                    key={link.name}
                                    href={link.href}
                                    className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                                >
                                    {link.name}
                                </a>
                            ))}
                        </div>
                    </div>

                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                        <span>Made with</span>
                        <Heart className="w-4 h-4 text-red-500 fill-current" />
                        <span>and</span>
                        <Coffee className="w-4 h-4 text-amber-600" />
                    </div>
                </div>

                {/* Status Indicator */}
                <div className="mt-6 pt-4 border-t border-border/50">
                    <div className="flex items-center justify-center space-x-2">
                        <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                            <span className="text-xs text-muted-foreground">All systems operational</span>
                        </div>
                        <Separator orientation="vertical" className="h-4" />
                        <Badge variant="outline" className="text-xs">
                            v1.0.0
                        </Badge>
                    </div>
                </div>
            </div>
        </footer>
    )
}
