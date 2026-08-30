"use client"

import * as React from "react"
import {cn} from "@/lib/utils"
import {File, Upload, X} from "lucide-react"
import {Button} from "@/components/ui/button"

interface FileInputProps extends Omit<React.ComponentProps<"input">, "type" | "onChange"> {
    onChange?: (file: File | null) => void
    onClear?: () => void
    accept?: string
    maxSize?: number
    showPreview?: boolean
    placeholder?: string
}

const FileInput = React.forwardRef<HTMLInputElement, FileInputProps>(
    ({className, onChange, onClear, accept, maxSize, showPreview = true, placeholder, ...props}, ref) => {
        const [selectedFile, setSelectedFile] = React.useState<File | null>(null)
        const [preview, setPreview] = React.useState<string | null>(null)
        const [isDragging, setIsDragging] = React.useState(false)
        const inputRef = React.useRef<HTMLInputElement>(null)

        React.useImperativeHandle(ref, () => inputRef.current!)

        const handleFileChange = (file: File | null) => {
            setSelectedFile(file)
            onChange?.(file)

            // Generate preview for images
            if (file && showPreview && file.type.startsWith("image/")) {
                const reader = new FileReader()
                reader.onloadend = () => {
                    setPreview(reader.result as string)
                }
                reader.readAsDataURL(file)
            } else {
                setPreview(null)
            }
        }

        const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
            const file = event.target.files?.[0] || null

            if (file && maxSize && file.size > maxSize) {
                alert(`File size must be less than ${maxSize / 1024 / 1024}MB`)
                return
            }

            handleFileChange(file)
        }

        const handleClear = () => {
            setSelectedFile(null)
            setPreview(null)
            if (inputRef.current) {
                inputRef.current.value = ""
            }
            onChange?.(null)
            onClear?.()
        }

        const handleDragOver = (e: React.DragEvent) => {
            e.preventDefault()
            setIsDragging(true)
        }

        const handleDragLeave = (e: React.DragEvent) => {
            e.preventDefault()
            setIsDragging(false)
        }

        const handleDrop = (e: React.DragEvent) => {
            e.preventDefault()
            setIsDragging(false)

            const file = e.dataTransfer.files?.[0] || null

            if (file && accept) {
                const acceptedTypes = accept.split(",").map((t) => t.trim())
                const isAccepted = acceptedTypes.some((type) => {
                    if (type.startsWith(".")) {
                        return file.name.endsWith(type)
                    }
                    return file.type.match(type.replace("*", ".*"))
                })

                if (!isAccepted) {
                    alert("File type not accepted")
                    return
                }
            }

            if (file && maxSize && file.size > maxSize) {
                alert(`File size must be less than ${maxSize / 1024 / 1024}MB`)
                return
            }

            handleFileChange(file)
        }

        const formatFileSize = (bytes: number) => {
            if (bytes === 0) return "0 Bytes"
            const k = 1024
            const sizes = ["Bytes", "KB", "MB", "GB"]
            const i = Math.floor(Math.log(bytes) / Math.log(k))
            return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
        }

        const {children, ...inputProps} = props

        return (
            <div className="w-full">
                <input
                    ref={inputRef}
                    type="file"
                    accept={accept}
                    onChange={handleInputChange}
                    className="sr-only"
                    {...inputProps}
                />

                {!selectedFile ? (
                    <div
                        onClick={() => inputRef.current?.click()}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        className={cn(
                            "border-input bg-background hover:bg-muted relative flex min-h-[120px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-8 text-center transition-colors",
                            isDragging && "border-primary bg-primary/5",
                            inputProps.disabled && "pointer-events-none opacity-50",
                            className,
                        )}
                    >
                        <Upload className="text-muted-foreground mb-3 h-8 w-8"/>
                        <div className="space-y-1">
                            <p className="text-sm font-medium">Charger un fichier</p>
                            {/*<p className="text-muted-foreground text-xs">
                                {accept ? `Accepted: ${accept}` : "Any file type"}
                                {maxSize && ` (Max ${maxSize / 1024 / 1024}MB)`}
                            </p>*/}
                            {
                                placeholder && (<p className={"text-sm text-muted-foreground"}>{placeholder}</p>)
                            }
                        </div>
                    </div>
                ) : (
                    <div className="border-input bg-card relative flex items-center gap-3 rounded-lg border p-4">
                        {preview ? (
                            <img src={preview || "/placeholder.svg"} alt="Preview"
                                 className="h-12 w-12 rounded object-cover"/>
                        ) : (
                            <div className="bg-muted flex h-12 w-12 items-center justify-center rounded">
                                <File className="text-muted-foreground h-6 w-6"/>
                            </div>
                        )}
                        <div className="flex-1 overflow-hidden">
                            <p className="truncate text-sm font-medium">{selectedFile.name}</p>
                            <p className="text-muted-foreground text-xs">{formatFileSize(selectedFile.size)}</p>
                        </div>
                        <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={handleClear}
                            disabled={inputProps.disabled}
                            className="h-8 w-8 shrink-0"
                        >
                            <X className="h-4 w-4"/>
                            <span className="sr-only">Clear file</span>
                        </Button>
                    </div>
                )}
            </div>
        )
    },
)

FileInput.displayName = "FileInput"

export {FileInput}
