export const isValidUrl = (url: string) => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

export const isPositiveNumber = (value: number) => {
  return typeof value === 'number' && value > 0
}

export const isNonNegativeNumber = (value: number) => {
  return typeof value === 'number' && value >= 0
} 