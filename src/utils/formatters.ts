export const formatCurrency = (value: string | number): string => {
  if (!value) return "R$ 0,00";
  
  try {
    const numericValue = typeof value === 'string' 
      ? parseFloat(value.replace(/[^\d,.-]/g, '').replace(',', '.'))
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

export const formatDate = (dateString: string): string => {
  if (!dateString) return "Data não informada";
  
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    }).format(date);
  } catch (e) {
    console.error("Error formatting date:", e, dateString);
    return "Data inválida";
  }
};

export const formatArea = (area: string | number): string => {
  if (!area) return "0 m²";
  
  try {
    const numericArea = typeof area === 'string'
      ? parseFloat(area.replace(/[^\d,.-]/g, '').replace(',', '.'))
      : area;
      
    if (isNaN(numericArea)) return "0 m²";
    
    return new Intl.NumberFormat('pt-BR', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(numericArea) + ' m²';
  } catch (e) {
    console.error("Error formatting area:", e, area);
    return "0 m²";
  }
}; 