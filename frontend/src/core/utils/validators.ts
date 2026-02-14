export const isEmail = (email: string) => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

export const isPhone = (phone: string) => {
  return /^\+?[\d\s-()]+$/.test(phone);
};

export const isRequired = (value: any) => {
  return value !== null && value !== undefined && value !== '';
};
