'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Modal from '@/components/shared/Modal'
import ModalForm from '@/components/shared/ModalForm'
import { useAuthenticatedFetch } from '@/hooks/useAuthenticatedFetch'

const editProjectSchema = z.object({
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

type EditProjectFormData = z.infer<typeof editProjectSchema>

interface Project {
  id: number
  name: string
  description?: string
  document_start_date: string
  document_end_date: string
  tenant_id: number
  created_at: string
  created_by?: string
  updated_at: string
  updated_by?: string
}

interface EditProjectModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  project: Project | null
}

export default function EditProjectModal({ isOpen, onClose, onSuccess, project }: EditProjectModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const { authenticatedFetch } = useAuthenticatedFetch()

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue
  } = useForm<EditProjectFormData>({
    resolver: zodResolver(editProjectSchema)
  })

  // Pre-populate form when project changes
  useEffect(() => {
    if (project && isOpen) {
      setValue('name', project.name)
      setValue('description', project.description || '')
      setValue('document_start_date', project.document_start_date.split('T')[0]) // Convert to date format
      setValue('document_end_date', project.document_end_date.split('T')[0]) // Convert to date format
    }
  }, [project, isOpen, setValue])

  const onSubmit = async (data: EditProjectFormData) => {
    if (!project) return

    try {
      setIsLoading(true)
      
      const response = await authenticatedFetch(`/api/projects/${project.id}`, {
        method: 'PUT',
        body: JSON.stringify(data)
      })

      if (response.ok) {
        onSuccess()
        onClose()
      }
    } catch (error) {
      console.error('Error updating project:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    reset()
    onClose()
  }

  if (!project) return null

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Edit Project"
      size="lg"
    >
      <form onSubmit={handleSubmit(onSubmit)}>
        <ModalForm
          onCancel={handleCancel}
          submitText="Update Project"
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