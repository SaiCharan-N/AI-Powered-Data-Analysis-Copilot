export function formatNumber(value) {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return value;
  }

  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 2,
  }).format(value);
}

export function getErrorMessage(error) {
  return (
    error?.response?.data?.detail ||
    error?.message ||
    "Something went wrong. Please try again."
  );
}

export function classNames(...values) {
  return values.filter(Boolean).join(" ");
}
