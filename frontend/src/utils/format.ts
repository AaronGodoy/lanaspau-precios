export const formatCurrency = (value?: number | null) =>
  new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP', maximumFractionDigits: 0 }).format(value ?? 0);

export const formatPercent = (value?: number | null) => `${(value ?? 0).toFixed(2)}%`;

export const formatDate = (value?: string | null) =>
  value ? new Intl.DateTimeFormat('es-CL', { dateStyle: 'medium' }).format(new Date(value)) : '-';
