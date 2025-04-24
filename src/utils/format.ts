export const formatCurrency = (value: string | number) => {
  if (!value) return "R$ 0,00";
  try {
    const numericValue = typeof value === 'string' 
      ? parseFloat(value.replace(/[^\d.-]/g, '').replace(',', '.'))
      : value;
      
    if (isNaN(numericValue)) return "R$ 0,00";
    return new Intl.NumberFormat('pt-BR', { 
      style: 'currency', 
      currency: 'BRL',
      maximumFractionDigits: 0
    }).format(numericValue);
  } catch (e) {
    console.error("Error formatting currency:", e, value);
    return "R$ 0,00";
  }
};

export const formatDate = (date: string | Date) => {
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    }).format(dateObj);
  } catch (e) {
    console.error("Error formatting date:", e, date);
    return "Data inválida";
  }
}; 