'use client';

import { AppShell } from '@/components/apple';
import SettingsPanel from '@/components/settings/settings-panel';

export default function SettingsPage() {
  return (
    <AppShell title="Preferences" statusBadge="Synced locally">
      <div className="py-4">
        <SettingsPanel />
      </div>
    </AppShell>
  );
}
