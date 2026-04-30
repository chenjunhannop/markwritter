import { BaseLayout } from "@/components/layouts/base-layout";
import { SettingsPage as SettingsPageContent } from "@/features/settings/settings-page";

export default function SettingsPage() {
  return (
    <BaseLayout>
      <SettingsPageContent />
    </BaseLayout>
  );
}
