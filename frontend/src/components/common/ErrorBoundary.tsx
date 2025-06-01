import React, { Component, ErrorInfo, ReactNode } from "react";
import { Card, CardBody, Typography, Button } from "@material-tailwind/react";
import { logger } from "../../utils/logger";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    logger.error("ErrorBoundary caught an error:", { error, errorInfo });
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <Card className="w-full">
          <CardBody className="text-center">
            <Typography variant="h5" color="red" className="mb-4">
              Something went wrong
            </Typography>
            <Typography color="gray" className="mb-4">
              {this.state.error?.message || "An unexpected error occurred"}
            </Typography>
            <Button color="blue" onClick={this.handleRetry}>
              Try Again
            </Button>
          </CardBody>
        </Card>
      );
    }

    return this.props.children;
  }
}
