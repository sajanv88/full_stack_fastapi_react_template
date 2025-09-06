import { Loading } from "@/components/shared/loading"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function LoadingDemo() {
    return (
        <div className="container mx-auto py-8 space-y-8">
            <div className="text-center">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Loading Components Demo</h1>
                <p className="text-gray-600">Different loading animations and styles</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Spinner Variants */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Spinner</CardTitle>
                        <CardDescription>Classic spinning loader</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-500 mb-2">Small</p>
                            <Loading variant="spinner" size="sm" />
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-gray-500 mb-2">Medium</p>
                            <Loading variant="spinner" size="md" />
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-gray-500 mb-2">Large with text</p>
                            <Loading variant="spinner" size="lg" text="Loading data..." />
                        </div>
                    </CardContent>
                </Card>

                {/* Dots Variants */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Bouncing Dots</CardTitle>
                        <CardDescription>Animated bouncing dots</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-500 mb-2">Small</p>
                            <Loading variant="dots" size="sm" />
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-gray-500 mb-2">Medium</p>
                            <Loading variant="dots" size="md" />
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-gray-500 mb-2">Large with text</p>
                            <Loading variant="dots" size="lg" text="Processing..." />
                        </div>
                    </CardContent>
                </Card>

                {/* Pulse Variants */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Gradient Pulse</CardTitle>
                        <CardDescription>Pulsing gradient circle</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="text-center">
                            <p className="text-sm text-gray-500 mb-2">Small</p>
                            <Loading variant="pulse" size="sm" />
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-gray-500 mb-2">Medium</p>
                            <Loading variant="pulse" size="md" />
                        </div>
                        <div className="text-center">
                            <p className="text-sm text-gray-500 mb-2">Large with text</p>
                            <Loading variant="pulse" size="lg" text="Saving changes..." />
                        </div>
                    </CardContent>
                </Card>

                {/* Skeleton Variants */}
                <Card>
                    <CardHeader>
                        <CardTitle className="text-lg">Skeleton</CardTitle>
                        <CardDescription>Content placeholder</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <p className="text-sm text-gray-500 mb-2">Text skeleton</p>
                            <Loading variant="skeleton" text="Loading content..." />
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Usage Examples */}
            <Card>
                <CardHeader>
                    <CardTitle>Usage Examples</CardTitle>
                    <CardDescription>How to use the Loading component in your code</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4 text-sm">
                        <div>
                            <h4 className="font-semibold mb-2">Basic Usage:</h4>
                            <code className="bg-gray-100 p-2 rounded block">
                                {`<Loading variant="spinner" size="md" text="Loading..." />`}
                            </code>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-2">Available Variants:</h4>
                            <ul className="list-disc list-inside space-y-1 text-gray-600">
                                <li><code>"spinner"</code> - Classic spinning circle</li>
                                <li><code>"dots"</code> - Three bouncing dots</li>
                                <li><code>"pulse"</code> - Gradient pulsing circle</li>
                                <li><code>"skeleton"</code> - Content placeholder bars</li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="font-semibold mb-2">Available Sizes:</h4>
                            <ul className="list-disc list-inside space-y-1 text-gray-600">
                                <li><code>"sm"</code> - Small size</li>
                                <li><code>"md"</code> - Medium size (default)</li>
                                <li><code>"lg"</code> - Large size</li>
                            </ul>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
