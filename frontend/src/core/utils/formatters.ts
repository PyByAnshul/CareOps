export const formatDate = (date: string | Date) => {
  return new Date(date).toLocaleDateString();
};

export const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
};

export const formatTime = (date: string | Date) => {
  return new Date(date).toLocaleTimeString();
};
