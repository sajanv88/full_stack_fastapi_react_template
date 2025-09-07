
export const validateImageFile = (file: File): { isValid: boolean; error?: string } => {
    if (!file.type.startsWith('image/')) {
        return { isValid: false, error: 'Please select a valid image file' }
    }

    const maxSize = 5 * 1024 * 1024 // 5MB
    if (file.size > maxSize) {
        return { isValid: false, error: 'Image size should be less than 5MB' }
    }

    return { isValid: true }
}

export const createImagePreview = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => {
            if (e.target?.result) {
                resolve(e.target.result as string)
            } else {
                reject(new Error('Failed to read file'))
            }
        }
        reader.onerror = () => reject(new Error('Failed to read file'))
        reader.readAsDataURL(file)
    })
}

export const compressImage = (
    file: File,
    maxWidth: number = 400,
    maxHeight: number = 400,
    quality: number = 0.8
): Promise<Blob> => {
    return new Promise((resolve) => {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')!
        const img = new Image()

        img.onload = () => {
            // Calculate new dimensions
            let { width, height } = img

            if (width > height) {
                if (width > maxWidth) {
                    height = (height * maxWidth) / width
                    width = maxWidth
                }
            } else {
                if (height > maxHeight) {
                    width = (width * maxHeight) / height
                    height = maxHeight
                }
            }

            canvas.width = width
            canvas.height = height

            // Draw and compress
            ctx.drawImage(img, 0, 0, width, height)
            canvas.toBlob((blob) => {
                if (blob) {
                    resolve(blob)
                } else {
                    resolve(new Blob())
                }
            }, 'image/jpeg', quality)
        }

        img.src = URL.createObjectURL(file)
    })
}

export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'

    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
