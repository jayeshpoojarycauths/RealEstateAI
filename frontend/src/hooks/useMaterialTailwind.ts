import {
  ButtonProps,
  CardProps,
  CardHeaderProps,
  CardBodyProps,
  TypographyProps,
  InputProps,
  SelectProps,
  SpinnerProps,
} from "@material-tailwind/react";

export const useMaterialTailwind = () => {
  const getButtonProps = (): Partial<ButtonProps> => ({
    className: 'bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded w-full justify-start',
  });

  const getCardProps = (): Partial<CardProps> => ({
    className: 'bg-white shadow-lg rounded-lg overflow-hidden',
  });

  const getCardHeaderProps = (): Partial<CardHeaderProps> => ({
    className: 'bg-gray-50 px-6 py-4 border-b border-gray-200',
  });

  const getCardBodyProps = (): Partial<CardBodyProps> => ({
    className: 'p-6',
  });

  const getTypographyProps = (): Partial<TypographyProps> => ({
    className: 'text-gray-900',
  });

  const getInputProps = (): Partial<InputProps> => ({
    className: 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
  });

  const getSelectProps = (): Partial<SelectProps> => ({
    className: 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
  });

  const getSpinnerProps = (): Partial<SpinnerProps> => ({
    className: 'h-8 w-8',
  });

  return {
    getButtonProps,
    getCardProps,
    getCardHeaderProps,
    getCardBodyProps,
    getTypographyProps,
    getInputProps,
    getSelectProps,
    getSpinnerProps,
  };
}; 