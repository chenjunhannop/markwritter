'use client';

import { MainLayout } from '@/components/layout';
import SettingsPanel from '@/components/settings/settings-panel';

export default function SettingsPage() {
  return (
    <MainLayout title="Settings">
      <SettingsPanel />
    </MainLayout>
  );
}
