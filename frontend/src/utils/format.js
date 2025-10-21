/**
 * Format large numbers with K/M/B suffixes.
 *
 * @param {string|number} value - The number to format
 * @returns {string} Formatted number with suffix
 *
 * Examples:
 *   formatNumber(1500) => "1.5K"
 *   formatNumber(36309000) => "36.3M"
 *   formatNumber(1200000000) => "1.2B"
 */
export function formatNumber(value) {
  const num = typeof value === 'string' ? parseFloat(value) : value

  if (isNaN(num)) {
    return '0'
  }

  if (num >= 1_000_000_000) {
    return (num / 1_000_000_000).toFixed(1) + 'B'
  }
  if (num >= 1_000_000) {
    return (num / 1_000_000).toFixed(1) + 'M'
  }
  if (num >= 1_000) {
    return (num / 1_000).toFixed(1) + 'K'
  }
  return num.toString()
}
