"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  children?: ReactNode;
  fallback?: ReactNode;
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
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex-1 bg-workspace flex flex-col items-center justify-center p-8 text-center h-[70vh]">
          <div className="h-12 w-12 rounded-2xl bg-red-500/10 flex items-center justify-center border border-red-500/20 mb-4">
            <AlertTriangle className="h-6 w-6 text-red-500" />
          </div>
          <h2 className="font-syne font-bold text-lg text-primaryText mb-2">
            Something went wrong
          </h2>
          <p className="text-xs text-secondaryText font-mono max-w-md mb-6 leading-relaxed">
            {this.state.error?.message || "An unexpected application error occurred."}
          </p>
          <Button
            onClick={this.handleReset}
            className="bg-slate-800 hover:bg-slate-700 text-primaryText font-bold text-xs px-6 py-2 rounded-lg border border-border"
          >
            Reload Page
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
