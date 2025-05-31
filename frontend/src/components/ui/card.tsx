import React from 'react';
import {
  Card as MTCard,
  CardHeader as MTCardHeader,
  CardBody as MTCardBody,
  CardFooter as MTCardFooter,
  Typography,
  IconButton,
  Button
} from '@material-tailwind/react';
import type { color as MTColor, variant as MTVariant } from '@material-tailwind/react/types/components/button';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../lib/utils';

const cardVariants = cva(
  'rounded-lg border bg-card text-card-foreground shadow-sm',
  {
    variants: {
      variant: {
        default: 'bg-white',
        secondary: 'bg-gray-50',
        gradient: 'bg-gradient-to-r from-blue-500 to-blue-700',
      },
      size: {
        default: 'p-6',
        compact: 'p-4',
        spacious: 'p-8',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  icon?: React.ReactNode;
  iconColor?: MTColor;
  gradient?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, size, icon, iconColor = 'blue', gradient, children, ...props }, ref) => {
    const defaultEventHandlers = {
      onPointerEnterCapture: () => {},
      onPointerLeaveCapture: () => {},
      onResize: () => {},
      onResizeCapture: () => {},
      placeholder: undefined
    };

    return (
      <MTCard
        ref={ref}
        className={cn(cardVariants({ variant, size }), className)}
        {...defaultEventHandlers}
        {...props}
      >
        {icon && (
          <div className="flex justify-center mb-4">
            <IconButton
              variant="gradient"
              size="lg"
              color={iconColor}
              className="pointer-events-none rounded-full"
              {...defaultEventHandlers}
            >
              {icon}
            </IconButton>
          </div>
        )}
        {children}
      </MTCard>
    );
  }
);
Card.displayName = 'Card';

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  gradient?: boolean;
}

const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, title, description, gradient, children, ...props }, ref) => {
    const defaultEventHandlers = {
      onPointerEnterCapture: () => {},
      onPointerLeaveCapture: () => {},
      onResize: () => {},
      onResizeCapture: () => {},
      placeholder: undefined
    };

    const titleColor: MTColor = gradient ? 'white' : 'blue-gray';
    const descriptionColor: MTColor = gradient ? 'white' : 'blue-gray';

    return (
      <MTCardHeader
        ref={ref}
        variant={gradient ? 'gradient' : undefined}
        color={gradient ? 'blue' : undefined}
        className={cn('mb-4', className)}
        {...defaultEventHandlers}
        {...props}
      >
        {title && (
          <Typography
            variant="h6"
            color={titleColor}
            className="mb-2"
            {...defaultEventHandlers}
          >
            {title}
          </Typography>
        )}
        {description && (
          <Typography
            variant="small"
            color={descriptionColor}
            className="font-normal"
            {...defaultEventHandlers}
          >
            {description}
          </Typography>
        )}
        {children}
      </MTCardHeader>
    );
  }
);
CardHeader.displayName = 'CardHeader';

interface CardBodyProps extends React.HTMLAttributes<HTMLDivElement> {}

const CardBody = React.forwardRef<HTMLDivElement, CardBodyProps>(
  ({ className, children, ...props }, ref) => {
    const defaultEventHandlers = {
      onPointerEnterCapture: () => {},
      onPointerLeaveCapture: () => {},
      onResize: () => {},
      onResizeCapture: () => {},
      placeholder: undefined
    };

    return (
      <MTCardBody
        ref={ref}
        className={cn('p-6', className)}
        {...defaultEventHandlers}
        {...props}
      >
        {children}
      </MTCardBody>
    );
  }
);
CardBody.displayName = 'CardBody';

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  action?: React.ReactNode;
}

const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, action, children, ...props }, ref) => {
    const defaultEventHandlers = {
      onPointerEnterCapture: () => {},
      onPointerLeaveCapture: () => {},
      onResize: () => {},
      onResizeCapture: () => {},
      placeholder: undefined
    };

    return (
      <MTCardFooter
        ref={ref}
        className={cn('flex items-center justify-between p-6 pt-0', className)}
        {...defaultEventHandlers}
        {...props}
      >
        {children}
        {action && (
          <div className="flex items-center gap-2">
            {action}
          </div>
        )}
      </MTCardFooter>
    );
  }
);
CardFooter.displayName = 'CardFooter';

export {
  Card,
  CardHeader,
  CardBody,
  CardFooter,
}; 