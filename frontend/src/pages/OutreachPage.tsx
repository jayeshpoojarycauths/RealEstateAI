import React from 'react';
import { LeadUpload } from '../components/outreach/LeadUpload';
import { OutreachLogs } from '../components/outreach/OutreachLogs';

export function OutreachPage() {
  return (
    <div className="container mx-auto p-4 space-y-8">
      <LeadUpload />
      <OutreachLogs />
    </div>
  );
} 