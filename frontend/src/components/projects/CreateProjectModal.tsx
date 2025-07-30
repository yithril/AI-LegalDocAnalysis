'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Modal from '@/components/shared/Modal'
import ModalForm from '@/components/shared/ModalForm'
import { useApiClient } from '@/lib/api-client'
import type { CreateProjectRequest } from '@/types/api'

const createProjectSchema = z.object({
  name: z.string().min(1, 'Project name is required').max(255, 'Project name must be less than 255 characters'),
  description: z.string().optional(),
  document_start_date: z.string().min(1, 'Start date is required'),
  document_end_date: z.string().min(1, 'End date is required'),
}).refine((data) => {
  if (data.document_start_date && data.document_end_date) {
    return new Date(data.document_end_date) > new Date(data.document_start_date)
  }
  return true
}, {
  message: "End date must be after start date",
  path: ["document_end_date"]
})

type CreateProjectFormData = z.infer<typeof createProjectSchema>

interface CreateProjectModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

export default function CreateProjectModal({ isOpen, onClose, onSuccess }: CreateProjectModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const apiClient = useApiClient()

  // Storage key for form persistence
  const STORAGE_KEY = 'create-project-form-data'

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch
  } = useForm<CreateProjectFormData>({
    resolver: zodResolver(createProjectSchema)
  })

  // Watch form values for auto-save
  const formValues = watch()

  // Auto-save form data to sessionStorage
  useEffect(() => {
    if (Object.keys(formValues).length > 0) {
      const hasData = Object.values(formValues).some(value => value && value !== '')
      if (hasData) {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(formValues))
      }
    }
  }, [formValues])

  // Load saved form data when modal opens
  useEffect(() => {
    if (isOpen) {
      const savedData = sessionStorage.getItem(STORAGE_KEY)
      if (savedData) {
        try {
          const parsedData = JSON.parse(savedData)
          reset(parsedData)
        } catch (error) {
          console.error('Error loading saved form data:', error)
          sessionStorage.removeItem(STORAGE_KEY)
        }
      }
    }
  }, [isOpen, reset])

  const clearSavedData = () => {
    sessionStorage.removeItem(STORAGE_KEY)
  }

  const onSubmit = async (data: CreateProjectFormData) => {
    try {
      setIsLoading(true)
      
      const createRequest: CreateProjectRequest = {
        name: data.name,
        description: data.description || '',
        document_start_date: data.document_start_date,
        document_end_date: data.document_end_date
      }

      await apiClient.createProject(createRequest)

      clearSavedData()
      reset()
      onSuccess()
      onClose()
    } catch (error) {
      console.error('Error creating project:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    clearSavedData()
    reset()
    onClose()
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create New Project"
      size="lg"
    >
      <form onSubmit={handleSubmit(onSubmit)}>
        <ModalForm
          onCancel={handleCancel}
          submitText="Create Project"
          isLoading={isLoading}
        >
          {/* Project Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium mb-1">
              Project Name *
            </label>
            <input
              {...register('name')}
              type="text"
              id="name"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter project name"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium mb-1">
              Description
            </label>
            <textarea
              {...register('description')}
              id="description"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter project description (optional)"
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
            )}
          </div>

          {/* Start Date */}
          <div>
            <label htmlFor="document_start_date" className="block text-sm font-medium mb-1">
              Start Date *
            </label>
            <input
              {...register('document_start_date')}
              type="date"
              id="document_start_date"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.document_start_date && (
              <p className="mt-1 text-sm text-red-600">{errors.document_start_date.message}</p>
            )}
          </div>

          {/* End Date */}
          <div>
            <label htmlFor="document_end_date" className="block text-sm font-medium mb-1">
              End Date *
            </label>
            <input
              {...register('document_end_date')}
              type="date"
              id="document_end_date"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {errors.document_end_date && (
              <p className="mt-1 text-sm text-red-600">{errors.document_end_date.message}</p>
            )}
          </div>
        </ModalForm>
      </form>
    </Modal>
  )
} 