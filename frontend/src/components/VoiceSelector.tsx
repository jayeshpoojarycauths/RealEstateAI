import React, { useState, useEffect } from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, Play, Stop } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

interface Voice {
  voice_id: string;
  name: string;
  category: string;
  description: string;
  preview_url?: string;
}

interface VoiceSelectorProps {
  value?: string;
  onChange: (voiceId: string) => void;
  className?: string;
}

export function VoiceSelector({ value, onChange, className }: VoiceSelectorProps) {
  const [voices, setVoices] = useState<Voice[]>([]);
  const [loading, setLoading] = useState(true);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [audio, setAudio] = useState<HTMLAudioElement | null>(null);
  const { toast } = useToast();

  const fetchVoices = React.useCallback(async () => {
    try {
      const response = await fetch('/api/v1/tts/voices');
      if (!response.ok) throw new Error('Failed to fetch voices');
      const data = await response.json();
      setVoices(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load voices. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchVoices();
  }, [fetchVoices]);

  const handlePreview = async (voiceId: string) => {
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }

    setPreviewLoading(true);
    try {
      const response = await fetch('/api/v1/tts/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: "Hello! This is a preview of my voice.",
          voice_id: voiceId,
        }),
      });

      if (!response.ok) throw new Error('Failed to generate preview');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const newAudio = new Audio(url);
      
      newAudio.onended = () => {
        URL.revokeObjectURL(url);
        setAudio(null);
      };

      setAudio(newAudio);
      newAudio.play();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate preview. Please try again.",
        variant: "destructive",
      });
    } finally {
      setPreviewLoading(false);
    }
  };

  const stopPreview = () => {
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
      setAudio(null);
    }
  };

  return (
    <Card className={className}>
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Voice</label>
            {value && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => audio ? stopPreview() : handlePreview(value)}
                disabled={previewLoading}
              >
                {previewLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : audio ? (
                  <Stop className="h-4 w-4" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
              </Button>
            )}
          </div>
          
          <Select
            value={value}
            onValueChange={onChange}
            disabled={loading}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select a voice" />
            </SelectTrigger>
            <SelectContent>
              {loading ? (
                <SelectItem value="loading" disabled>
                  Loading voices...
                </SelectItem>
              ) : (
                voices.map((voice) => (
                  <SelectItem key={voice.voice_id} value={voice.voice_id}>
                    <div className="flex flex-col">
                      <span>{voice.name}</span>
                      <span className="text-xs text-muted-foreground">
                        {voice.category}
                      </span>
                    </div>
                  </SelectItem>
                ))
              )}
            </SelectContent>
          </Select>
        </div>
      </CardContent>
    </Card>
  );
} 