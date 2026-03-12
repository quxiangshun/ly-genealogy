export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase as string

  const getHeaders = (): Record<string, string> => {
    const headers: Record<string, string> = {}
    if (import.meta.client) {
      const token = localStorage.getItem('auth_token')
      if (token) headers['Authorization'] = `Bearer ${token}`
    }
    return headers
  }

  const api = <T>(url: string, opts?: Parameters<typeof $fetch>[1]) =>
    $fetch<T>(`${apiBase}/api${url}`, {
      ...opts,
      headers: { ...getHeaders(), ...(opts?.headers as Record<string, string>) },
    })

  return { api }
}
