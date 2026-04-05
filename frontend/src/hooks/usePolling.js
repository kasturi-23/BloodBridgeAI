import { useEffect, useRef } from 'react'

export function usePolling(fn, intervalMs = 5000, enabled = true) {
  const savedFn = useRef(fn)

  useEffect(() => {
    savedFn.current = fn
  }, [fn])

  useEffect(() => {
    if (!enabled) return
    savedFn.current()
    const id = setInterval(() => savedFn.current(), intervalMs)
    return () => clearInterval(id)
  }, [intervalMs, enabled])
}
