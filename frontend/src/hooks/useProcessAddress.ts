import { useMutation } from '@tanstack/react-query'
import { processAddress, type Addon } from '../api/client'

export type ProcessPayload = { raw: string; addons?: Addon[] | 'all' | 'none' }

export function useProcessAddress() {
  return useMutation({
    mutationKey: ['process-address'],
    mutationFn: (payload: ProcessPayload) => processAddress(payload.raw, payload.addons)
  })
}
