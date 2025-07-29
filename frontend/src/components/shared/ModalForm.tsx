'use client'

import { useTheme } from '@/components/providers/ThemeProvider'

interface ModalFormProps {
  children: React.ReactNode
  submitText?: string
  cancelText?: string
  onCancel?: () => void
  isLoading?: boolean
}

export default function ModalForm({ 
  children, 
  submitText = 'Save', 
  cancelText = 'Cancel',
  onCancel,
  isLoading = false
}: ModalFormProps) {
  const { theme } = useTheme()

  return (
    <div className="space-y-6">
      {/* Form Content */}
      <div className="space-y-4">
        {children}
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium rounded-md border border-gray-300 hover:bg-gray-50 transition-colors"
            style={{ color: theme.textColor }}
            disabled={isLoading}
          >
            {cancelText}
          </button>
        )}
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white rounded-md hover:opacity-90 transition-opacity disabled:opacity-50"
          style={{ backgroundColor: theme.accentColor }}
          disabled={isLoading}
        >
          {isLoading ? 'Saving...' : submitText}
        </button>
      </div>
    </div>
  )
} 