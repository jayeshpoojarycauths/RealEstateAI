import React from "react";
import {
  Spinner,
  Typography,
  Button,
  Card,
  CardHeader,
  CardBody,
  Dialog,
  DialogHeader,
  DialogBody,
  DialogFooter,
  Input,
  Select,
  Option,
  Alert,
} from "@material-tailwind/react";

const noOp = () => {};
const defaultProps = {
  onResize: noOp,
  onResizeCapture: noOp,
  onPointerEnterCapture: noOp,
  onPointerLeaveCapture: noOp,
  placeholder: "",
};

export const SafeSpinner = React.forwardRef((props: any, ref) => (
  <Spinner ref={ref} {...defaultProps} {...props} />
));

export const SafeTypography = React.forwardRef((props: any, ref) => (
  <Typography ref={ref} {...defaultProps} {...props} />
));

export const SafeButton = React.forwardRef((props: any, ref) => (
  <Button ref={ref} {...defaultProps} {...props} />
));

export const SafeCard = React.forwardRef((props: any, ref) => (
  <Card ref={ref} {...defaultProps} {...props} />
));

export const SafeCardHeader = React.forwardRef((props: any, ref) => (
  <CardHeader ref={ref} {...defaultProps} {...props} />
));

export const SafeCardBody = React.forwardRef((props: any, ref) => (
  <CardBody ref={ref} {...defaultProps} {...props} />
));

export const SafeDialog = React.forwardRef((props: any, ref) => (
  <Dialog ref={ref} {...defaultProps} {...props} />
));

export const SafeDialogHeader = React.forwardRef((props: any, ref) => (
  <DialogHeader ref={ref} {...defaultProps} {...props} />
));

export const SafeDialogBody = React.forwardRef((props: any, ref) => (
  <DialogBody ref={ref} {...defaultProps} {...props} />
));

export const SafeDialogFooter = React.forwardRef((props: any, ref) => (
  <DialogFooter ref={ref} {...defaultProps} {...props} />
));

export const SafeInput = React.forwardRef((props: any, ref) => (
  <Input ref={ref} {...defaultProps} {...props} />
));

export const SafeSelect = React.forwardRef((props: any, ref) => (
  <Select ref={ref} {...defaultProps} {...props} />
));

export const SafeOption = React.forwardRef((props: any, ref) => (
  <Option ref={ref} {...defaultProps} {...props} />
));

export const SafeAlert = React.forwardRef((props: any, ref) => (
  <Alert ref={ref} {...defaultProps} {...props} />
)); 