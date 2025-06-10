# Material Tailwind Setup and Usage Guide

## Overview

This project uses Material Tailwind (MTW) as its primary UI component library, combined with Tailwind CSS for custom styling. The setup includes custom wrappers and hooks to ensure type safety and consistent usage across the application.

## Core Components

### 1. SafeMTW Wrapper (`src/components/SafeMTW.tsx`)

The `SafeMTW` wrapper provides a type-safe way to use Material Tailwind components by:
- Handling common prop issues
- Managing refs properly
- Providing consistent default props

```typescript
// Example of a wrapped component
export const SafeButton = React.forwardRef((props: any, ref) => (
  <Button ref={ref} {...defaultProps} {...props} />
));
```

Available wrapped components:
- `SafeSpinner`
- `SafeTypography`
- `SafeButton`
- `SafeCard` / `SafeCardHeader` / `SafeCardBody`
- `SafeDialog` / `SafeDialogHeader` / `SafeDialogBody` / `SafeDialogFooter`
- `SafeInput`
- `SafeSelect` / `SafeOption`
- `SafeAlert`
- `SafeSwitch`
- `SafeIconButton`
- `SafeDrawer`
- `SafeList` / `SafeListItem` / `SafeListItemPrefix`

### 2. Material Tailwind Hook (`src/hooks/useMaterialTailwind.ts`)

The `useMaterialTailwind` hook provides type-safe props for MTW components:

```typescript
const { getButtonProps, getCardProps, getTypographyProps } = useMaterialTailwind();

// Usage
<SafeButton {...getButtonProps()}>
  Click Me
</SafeButton>
```

## Styling Patterns

### 1. Component Usage

```tsx
// Using Material Tailwind components with custom props
<SafeTypography 
  variant="h5" 
  color="blue" 
  {...getTypographyProps()}
>
  Real Estate AI
</SafeTypography>

// Using Tailwind classes for layout and custom styling
<div className="flex h-screen bg-gray-100">
  {/* Content */}
</div>
```

### 2. Layout Structure

The project follows a consistent layout pattern:
- `DashboardLayout.tsx` - Main application layout
- `SimpleLayout.tsx` - Simplified layout for auth pages
- Each layout combines MTW components with Tailwind classes

## Best Practices

1. **Component Imports**
   ```typescript
   import {
     SafeTypography,
     SafeButton,
     SafeCard,
     SafeCardBody,
   } from "../components/SafeMTW";
   ```

2. **Icon Usage**
   ```typescript
   import { 
     HomeIcon,
     UserGroupIcon,
     // ... other icons
   } from "@heroicons/react/24/outline";
   ```

3. **Styling Approach**
   - Use MTW components for UI elements (buttons, cards, etc.)
   - Use Tailwind classes for:
     - Layout (`flex`, `grid`, etc.)
     - Spacing (`p-4`, `m-2`, etc.)
     - Custom styling not covered by MTW

4. **Type Safety**
   - Always use the `SafeMTW` components instead of direct MTW imports
   - Use the `useMaterialTailwind` hook for component props
   - Maintain proper TypeScript types for custom components

## Example Implementation

```tsx
import React from "react";
import {
  SafeTypography,
  SafeButton,
  SafeCard,
  SafeCardBody,
} from "../components/SafeMTW";
import { useMaterialTailwind } from "../hooks/useMaterialTailwind";

const ExampleComponent: React.FC = () => {
  const { getButtonProps, getCardProps, getTypographyProps } = useMaterialTailwind();

  return (
    <div className="p-4">
      <SafeCard {...getCardProps()}>
        <SafeCardBody>
          <SafeTypography variant="h4" {...getTypographyProps()}>
            Example Title
          </SafeTypography>
          <SafeButton 
            color="blue" 
            variant="filled"
            {...getButtonProps()}
          >
            Click Me
          </SafeButton>
        </SafeCardBody>
      </SafeCard>
    </div>
  );
};
```

## Configuration

The project uses the following configuration files:
- `tailwind.config.js` - Tailwind CSS configuration
- `postcss.config.js` - PostCSS configuration for processing CSS

## Common Patterns

1. **Navigation Items**
   ```typescript
   const navItems = [
     {
       path: "/dashboard",
       icon: <HomeIcon className="h-5 w-5" />,
       label: "Dashboard",
     },
     // ... more items
   ];
   ```

2. **Active State Handling**
   ```typescript
   const isActive = (path: string) => {
     return location.pathname === path;
   };
   ```

3. **Responsive Design**
   ```typescript
   <div className="md:hidden"> {/* Mobile only */}</div>
   <div className="hidden md:block"> {/* Desktop only */}</div>
   ```

## Troubleshooting

1. **Component Not Rendering**
   - Ensure you're using the `SafeMTW` wrapper
   - Check if you've included the necessary props from `useMaterialTailwind`

2. **Styling Issues**
   - Verify Tailwind classes are being applied
   - Check for conflicting styles between MTW and Tailwind

3. **Type Errors**
   - Use the correct prop types from `SafeMTW`
   - Ensure proper usage of the `useMaterialTailwind` hook 